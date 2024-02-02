from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path
import pickle
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, TypeVar
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta
from marshmallow import fields, post_dump, post_load, \
    Schema, validate, validates_schema
from marshmallow.exceptions import ValidationError
import numpy
import pandas
from sqlalchemy import MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename

from viime.colors import category10
from viime.imputation import IMPUTE_MCAR_METHODS, impute_missing, IMPUTE_MNAR_METHODS
from viime.normalization import NORMALIZATION_METHODS, normalize
from viime.scaling import scale, SCALING_METHODS
from viime.table_validation import get_fatal_index_errors, get_validation_list
from viime.transformation import transform, TRANSFORMATION_METHODS


# This is to avoid having to manually name all constraints
# See: http://alembic.zzzcomputing.com/en/latest/naming.html
metadata = MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
})
db = SQLAlchemy(metadata=metadata, engine_options={'connect_args': {'timeout': 1000}})
BaseModel: DefaultMeta = db.Model

AxisNameTypes = namedtuple('AxisNameTypes', ['ROW', 'COLUMN'])
TableColumnTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK', 'GROUP'])
TableRowTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK'])
MetaDataTypes = namedtuple('MetaDataTypes', ['CATEGORICAL', 'NUMERICAL', 'ORDINAL'])
TABLE_COLUMN_TYPES = TableColumnTypes('key', 'metadata', 'measurement', 'masked', 'group')
TABLE_ROW_TYPES = TableRowTypes('header', 'metadata', 'sample', 'masked')
AXIS_NAME_TYPES = AxisNameTypes('row', 'column')
METADATA_TYPES = MetaDataTypes('categorical', 'numerical', 'ordinal')

T = TypeVar('T')


def clean(df: pandas.DataFrame) -> pandas.DataFrame:
    return df.fillna('NaN') \
        .replace([numpy.Inf, -numpy.Inf], ['Inf', '-Inf'])


def _guess_table_structure(table: pandas.DataFrame) -> Tuple[List[str], List[str]]:
    """Infer table structure by inspecting data.

    For simplicity, this method assumes the key row/column is always first.  This
    appears to be true for the vast majority of cases.
    """
    rows: List[str] = [TABLE_ROW_TYPES.INDEX]
    columns: List[str] = [TABLE_COLUMN_TYPES.INDEX]

    # mask any row that is either all strings (or nan's) or has 0 variance
    for i in range(1, table.shape[0]):
        row_variance = pandas.to_numeric(table.iloc[i, 1:], errors='coerce').var()
        if row_variance != row_variance or row_variance == 0:
            rows.append(TABLE_ROW_TYPES.MASK)
        else:
            rows.append(TABLE_ROW_TYPES.DATA)

    # mask any column that is either all strings (or nan's) or has 0 variance
    # the first such column is marked as the group
    has_group = False
    for i in range(1, table.shape[1]):
        column_variance = pandas.to_numeric(table.iloc[1:, i], errors='coerce').var()
        if column_variance != column_variance and not has_group:
            has_group = True
            columns.append(TABLE_COLUMN_TYPES.GROUP)
        elif column_variance != column_variance or column_variance == 0:
            columns.append(TABLE_COLUMN_TYPES.MASK)
        else:
            columns.append(TABLE_COLUMN_TYPES.DATA)

    # fall back to setting the second column as the group column as was
    # done before
    if not has_group:
        columns[1] = TABLE_COLUMN_TYPES.GROUP

    return rows, columns


class BaseSchema(Schema):
    __model__ = None

    @post_load
    def make_object(self, data, **kwargs):
        if self.__model__ is not None:
            return self.__model__(**data)
        return data


class GroupLevel(BaseModel):
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    name = db.Column(db.String, primary_key=True)
    color = db.Column(db.String, nullable=False)
    label = db.Column(db.String)
    description = db.Column(db.String)


class GroupLevelSchema(BaseSchema):
    __model__ = GroupLevel  # type: ignore

    csv_file_id = fields.UUID(required=True, load_only=True)
    name = fields.Str(required=True)
    color = fields.Str(required=True)
    label = fields.Str()
    description = fields.Str(allow_none=True)


class CSVFile(BaseModel):
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    imputation_mnar = db.Column(db.String, nullable=False)
    imputation_mcar = db.Column(db.String, nullable=False)
    meta = db.Column(JSONType, nullable=False)
    selected_columns = db.Column(db.PickleType, nullable=True)
    group_levels = relationship('GroupLevel', cascade='all, delete, delete-orphan, expunge')

    sample_group = db.Column(db.String, nullable=True)
    sample_group_obj = relationship('SampleGroup', backref='files',
                                    primaryjoin='foreign(CSVFile.sample_group) == '
                                                'remote(SampleGroup.name)',
                                    order_by='CSVFile.name')

    column_json = db.Column(JSONType, nullable=False, default=list)
    row_json = db.Column(JSONType, nullable=False, default=list)

    @property
    def columns(self):
        if self.column_json is not None:
            flag_modified(self, 'column_json')
            return self.column_json
        else:
            return []

    @property
    def rows(self):
        if self.row_json is not None:
            flag_modified(self, 'row_json')
            return self.row_json
        else:
            return []

    @property
    def table_validation(self):
        """Return a list of issues with the table or None if everything is okay."""
        try:
            return get_validation_list(self)
        except Exception:
            current_app.logger.exception('Error performing table validation')
            raise

    @property
    def table(self):
        return pandas.read_csv(self.uri, index_col=None, header=None)

    @property
    def indexed_table(self):
        kwargs: Dict[str, Any] = {}

        # handle column names
        header_row = self.header_row_index
        kwargs['header'] = header_row
        if header_row is None:
            kwargs['names'] = self.headers

        # handle row ids
        kwargs['index_col'] = False
        key_column = self.key_column_index
        if key_column is not None:
            kwargs['index_col'] = key_column

        indexed_table = pandas.read_csv(self.uri, **kwargs)

        # inject the computed keys in case the csv file does not have a primary key column
        if key_column is None:
            keys = self.keys

            # exclude the header row from the primary key index if present
            if header_row is not None:
                keys = keys[1:]
            indexed_table.index = pandas.Index(keys)

        return indexed_table

    @property
    def measurement_table(self):
        """Return the processed metabolite date table."""
        return self.measurement_table_and_info[0]

    @property
    def measurement_table_and_info(self):
        """Return the processed metabolite date table."""
        try:
            if not get_fatal_index_errors(self):
                try:
                    return self.apply_transforms()
                except Exception as e:
                    # TODO: We should handle this better
                    current_app.logger.exception(e)
            return None, dict(mcar=[], mnar=[])
        except Exception:
            current_app.logger.exception('Error getting measurement_table')
            raise

    @property
    def measurement_metadata(self):
        """Return metadata rows."""
        return self.filter_table_by_types(TABLE_ROW_TYPES.METADATA, TABLE_COLUMN_TYPES.DATA)

    @property
    def sample_metadata(self):
        """Return metadata columns."""
        return self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.METADATA)

    @property
    def raw_measurement_table(self):
        """Return the metabolite data table before transformation."""
        return self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.DATA)

    @property
    def groups(self):
        """Return a table containing the primary grouping column."""
        if self.group_column_index is None:
            return None
        groups = self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.GROUP)
        if groups is None:
            return None
        # ensure groups are strings
        return groups.fillna('').astype(str)

    @property
    def uri(self) -> Path:
        id = str(self.id)
        return Path(current_app.config['UPLOAD_FOLDER']) / id[:3] / id

    @property
    def size(self) -> int:
        return Path(self.uri).stat().st_size

    @property
    def header_row_index(self):
        row = self.find_first_entity(
            lambda r: r['row_type'] == TABLE_ROW_TYPES.INDEX, self.rows)
        return row and row['row_index']

    @header_row_index.setter  # type: ignore
    def header_row_index(self, value: Optional[int]):
        if self.header_row_index is not None:
            old_row = self.rows[self.header_row_index]
            old_row['row_type'] = TABLE_ROW_TYPES.METADATA

            db.session.add(self)

        if value is not None:
            new_row = self.rows[value]
            new_row['row_type'] = TABLE_ROW_TYPES.INDEX

            db.session.add(self)

    @property
    def headers(self):
        return self._headers()

    def _headers(self, header_row_index=None):
        idx = self.header_row_index or header_row_index
        if idx is None:
            return [
                f'col{i + 1}' for i in range(self.table.shape[1])
            ]

        return list(self.table.iloc[idx, :])

    @property
    def key_column_index(self):
        column = self.find_first_entity(
            lambda c: c['column_type'] == TABLE_COLUMN_TYPES.INDEX, self.columns)
        return column and column['column_index']

    @key_column_index.setter  # type: ignore
    def key_column_index(self, value: Optional[int]):
        columns = self.columns
        if self.key_column_index is not None:
            old_column = columns[self.key_column_index]
            old_column['column_type'] = TABLE_COLUMN_TYPES.METADATA

            db.session.add(self)

        if value is not None:
            new_column = columns[value]
            new_column['column_type'] = TABLE_COLUMN_TYPES.INDEX

            db.session.add(self)

    @property
    def group_column_index(self):
        column = self.find_first_entity(
            lambda c: c['column_type'] == TABLE_COLUMN_TYPES.GROUP, self.columns)
        return column and column['column_index']

    @group_column_index.setter  # type: ignore
    def group_column_index(self, value: Optional[int]):
        columns = self.columns
        if self.group_column_index is not None:
            old_column = columns[self.group_column_index]
            old_column['column_type'] = TABLE_COLUMN_TYPES.METADATA

            db.session.add(self)

            self.group_levels = []

        if value is not None:
            new_column = columns[value]
            new_column['column_type'] = TABLE_COLUMN_TYPES.GROUP

            db.session.add(self)

            self.derive_group_levels()

    def derive_group_levels(self):
        groups = self.groups
        if groups is None or groups.empty:
            self.group_levels = []
            return
        levels = sorted([str(v) for v in groups.iloc[:, 0].unique()])
        self.group_levels = [GroupLevel(name=l, label=l, color=color)
                             for i, (l, color) in enumerate(zip(levels, category10()))]

    @property
    def keys(self):
        return self._keys()

    def _keys(self, key_column_index=None):
        idx = self.key_column_index or key_column_index
        if idx is None:
            return [
                f'row{i + 1}' for i in range(self.table.shape[0])
            ]
        return list(self.table.iloc[:, idx])

    def filter_table_by_types(self, row_type, column_type):
        if self.header_row_index is None or \
                self.key_column_index is None:
            return None
        rows = [
            row['row_index'] for row in self.rows
            if row['row_type'] == row_type
        ]
        if self.header_row_index is not None:
            rows = [self.header_row_index] + rows
        else:
            current_app.logger.warning('No header row is set.')

        columns = [
            column['column_index'] for column in self.columns
            if column['column_type'] == column_type
        ]
        if self.key_column_index is not None:
            index_col = 0
            columns = [self.key_column_index] + columns
        else:
            index_col = None

        return pandas.read_csv(
            BytesIO(
                self.table.iloc[rows, columns].to_csv(header=False, index=False).encode()
            ), index_col=index_col
        )

    @property
    def missing_cells(self) -> List[Tuple[int, int]]:
        table = self._coerce_numeric()
        col, row = numpy.nonzero(table.isna().to_numpy())
        return numpy.column_stack((row, col)).astype(int).tolist()

    def apply_transforms(self) -> pandas.DataFrame:
        table = self.raw_measurement_table
        table = self._coerce_numeric()
        return impute_missing(table, self.groups,
                              mnar=self.imputation_mnar, mcar=self.imputation_mcar)

    def save_table(self, table: pandas.DataFrame, **kwargs):
        # TODO: Delete cache entries if a file at self.uri exists already
        # For now, there is no API for changing the data contained in an uploaded
        # file, so this is not important.
        return self._save_csv_file_data(self.uri, table.to_csv(**kwargs))

    @property
    def _stats(self):
        if self.raw_measurement_table is not None:
            return self._get_table_stats()

    @classmethod
    def create_csv_file(cls, id: str, name: str, table: str, **kwargs):
        csv_file = cls(id=id, name=name, **kwargs)
        cls._save_csv_file_data(csv_file.uri, table)
        row_types, column_types = _guess_table_structure(csv_file.table)

        header_row_index = row_types.index(TABLE_ROW_TYPES.INDEX)
        headers = csv_file._headers(header_row_index)
        columns = []
        last_data_column_index = 0
        for index, column_type in enumerate(column_types):
            data_column_index = None
            if column_type == TABLE_COLUMN_TYPES.DATA:
                last_data_column_index += 1
                data_column_index = last_data_column_index

            columns.append({
                'meta': {},
                'subtype': None,
                'column_index': index,
                'column_type': column_type,
                'column_header': headers[index],
                'data_column_index': data_column_index
            })

        # do something similar for the rows
        key_column_index = column_types.index(TABLE_COLUMN_TYPES.INDEX)
        keys = csv_file._keys(key_column_index)
        rows = []
        last_data_row_index = 0
        for index, row_type in enumerate(row_types):
            data_row_index = None
            if row_type == TABLE_ROW_TYPES.DATA:
                last_data_row_index += 1
                data_row_index = last_data_row_index
            rows.append({
                'meta': {},
                'subtype': None,
                'row_index': index,
                'row_type': row_type,
                'row_name': keys[index],
                'data_row_index': data_row_index
            })

        table_column_schema = TableColumnSchema()
        csv_file.column_json = table_column_schema.dump(columns, many=True)
        table_row_schema = TableRowSchema()
        csv_file.row_json = table_row_schema.dump(rows, many=True)

        csv_file.derive_group_levels()
        return csv_file, rows, columns

    @classmethod
    def _save_csv_file_data(cls, uri: Path, table_data: str) -> str:
        uri.parent.mkdir(parents=True, exist_ok=True)
        with open(uri, 'w') as f:
            f.write(table_data)
        return table_data

    def get_column_by_name(self, column_name: str):
        return self.find_first_entity(lambda c: c['column_header'] == column_name, self.columns)

    def get_row_by_name(self, row_name):
        return self.find_first_entity(lambda r: r['row_name'] == row_name, self.rows)

    @classmethod
    def find_first_entity(cls, criterion: Callable[[T], bool],
                          iterable: Iterable[T]) -> Optional[T]:
        for entity in iterable:
            if criterion(entity):
                return entity
        return None

    def _get_table_stats(self):
        table = self.raw_measurement_table
        # Get global stats all once because it is more efficient than
        # doing it per row/column.

        # Once validation is done on indices we can get variance with:
        #   table.var(axis=?).to_list()
        # for now we need to do it per row/column
        def get_variance(series):
            return pandas.to_numeric(series, errors='coerce').var()

        def get_nan(series):
            s = pandas.to_numeric(series, errors='coerce')
            return (s != s).sum() / s.shape[0]

        column_missing = [get_nan(table.iloc[:, i]) for i in range(table.shape[1])]
        column_variance = [get_variance(table.iloc[:, i]) for i in range(table.shape[1])]
        row_missing = [get_nan(table.iloc[i, :]) for i in range(table.shape[0])]
        row_variance = [get_variance(table.iloc[i, :]) for i in range(table.shape[0])]
        return {
            'columns': {
                'missing': column_missing,
                'variance': column_variance
            },
            'rows': {
                'missing': row_missing,
                'variance': row_variance
            }
        }

    def _coerce_numeric(self) -> pandas.DataFrame:
        """Coerce a table into numeric values."""
        table = self.raw_measurement_table
        for i in range(table.shape[1]):
            table.iloc[:, i] = pandas.to_numeric(table.iloc[:, i], errors='coerce')
        return table

    def _get_csv_file_stats(self):
        if self.raw_measurement_table is not None:
            return self._get_table_stats()


def _validate_table_data(table: str):
    try:
        pandas.read_csv(BytesIO(table.encode()))
    except Exception as e:
        raise ValidationError(str(e).strip(), data=dict(table=table), field_name='table') from None


class CSVFileSchema(BaseSchema):
    id = fields.UUID(missing=uuid4)
    created = fields.DateTime(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    table = fields.Raw(required=True, validate=_validate_table_data)
    imputation_mnar = fields.Str(missing='zero', validate=validate.OneOf(IMPUTE_MNAR_METHODS))
    imputation_mcar = fields.Str(
        missing='random-forest', validate=validate.OneOf(IMPUTE_MCAR_METHODS))
    meta = fields.Dict(missing=dict)

    columns = fields.List(fields.Nested('TableColumnSchema'))
    rows = fields.List(fields.Nested('TableRowSchema'))

    selected_columns = fields.List(fields.Str(), dump_only=True, missing=list)
    group_levels = fields.List(fields.Nested('GroupLevelSchema'))

    # don't add `sample_group` since it is hidden internal property

    table_validation = fields.Nested('ValidationSchema', many=True, dump_only=True)
    # imputed measurements
    measurement_table = fields.Raw(dump_only=True, allow_none=True)
    missing_cells = fields.Raw(dump_only=True, allow_none=True)
    size = fields.Int(dump_only=True)

    @post_load
    def fix_file_name(self, data, **kwargs):
        data['name'] = secure_filename(data['name'])
        return data

    @post_dump
    def read_csv_file(self, data, **kwargs):
        if 'table' not in data:
            return data
        data['table'] = data['table'].to_csv(header=False, index=False)
        if data.get('measurement_table') is not None:
            data['measurement_table'] = clean(data['measurement_table']).to_dict(
                orient='split')
        return data

    @post_load
    def make_object(self, data, **kwargs):
        csv_file, rows, columns = CSVFile.create_csv_file(**data)
        db.session.add(csv_file)
        return csv_file


class SampleGroup(BaseModel):
    __allow_unmapped__ = True
    name = db.Column(db.String, primary_key=True)
    description = db.Column(db.String, nullable=True)
    order = db.Column(db.Integer, nullable=True)
    files: List[CSVFile]


class SampleGroupSchema(BaseSchema):
    __model__ = SampleGroup  # type: ignore

    name = fields.String(required=True)
    description = fields.Str(allow_none=True)
    files = fields.List(fields.Nested(CSVFileSchema, only=['id', 'name', 'description']))


class TableColumnSchema(BaseSchema):
    csv_file_id = fields.UUID(required=True, load_only=True)
    column_header = fields.Str(dump_only=True)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    subtype = fields.Str(required=False, validate=validate.OneOf(METADATA_TYPES))
    meta = fields.Dict(missing=dict)


class TableRowSchema(BaseSchema):
    csv_file_id = fields.UUID(required=True, load_only=True)
    row_name = fields.Str(dump_only=True)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    subtype = fields.Str(required=False, validate=validate.OneOf(METADATA_TYPES))
    meta = fields.Dict(missing=dict)


class ModifyLabelChangesSchema(Schema):
    context = fields.Str(required=True, validate=validate.OneOf(AXIS_NAME_TYPES))  # type: ignore
    index = fields.Int(required=True, validate=validate.Range(min=0))
    label = fields.Str(required=True)

    @validates_schema
    def validate_label(self, data, **kwargs):
        context = data['context']
        label = data['label']
        if context == AXIS_NAME_TYPES.COLUMN:
            if label not in TABLE_COLUMN_TYPES:
                raise ValidationError('label {} unrecognized'.format(label))
        elif context == AXIS_NAME_TYPES.ROW:
            if label not in TABLE_ROW_TYPES:
                raise ValidationError('label {} unrecognized'.format(label))
        else:
            raise ValidationError('context {} unrecognized'.format(context))


class ModifyLabelListSchema(Schema):
    changes = fields.List(fields.Nested(ModifyLabelChangesSchema), required=True)


class ValidatedMetaboliteTable(BaseModel):
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), nullable=False,
                            index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    normalization = db.Column(db.String, nullable=True)
    normalization_argument = db.Column(db.String, nullable=True)
    transformation = db.Column(db.String, nullable=True)
    scaling = db.Column(db.String, nullable=True)
    imputation_info = db.Column(JSONType, nullable=True)
    meta = db.Column(JSONType, nullable=False)

    raw_measurements_bytes = db.Column(db.LargeBinary, nullable=False)
    measurement_metadata_bytes = db.Column(db.LargeBinary, nullable=False)
    sample_metadata_bytes = db.Column(db.LargeBinary, nullable=False)
    groups_bytes = db.Column(db.LargeBinary, nullable=False)

    @classmethod
    def serialize_table(cls, table: pandas.DataFrame) -> bytes:
        return pickle.dumps(table)

    @classmethod
    def deserialize_table(cls, blob: bytes) -> pandas.DataFrame:
        return pickle.loads(blob)

    @classmethod
    def create_from_csv_file(cls, csv_file: CSVFile, **kwargs):
        table, info = csv_file.measurement_table_and_info
        assert table is not None, 'Invalid csv_file provided'

        attributes = {
            'id': uuid4(),
            'csv_file_id': csv_file.id,
            'name': csv_file.name,
            'meta': csv_file.meta.copy(),
            'raw_measurements_bytes': cls.serialize_table(table),
            'imputation_info': info,
            'measurement_metadata_bytes': cls.serialize_table(csv_file.measurement_metadata),
            'sample_metadata_bytes': cls.serialize_table(csv_file.sample_metadata),
            'groups_bytes': cls.serialize_table(csv_file.groups)
        }
        attributes.update(kwargs)
        return cls(**attributes)

    @property
    def raw_measurements(self):
        return self.deserialize_table(self.raw_measurements_bytes)

    @property
    def measurement_metadata(self):
        return self.deserialize_table(self.measurement_metadata_bytes)

    @property
    def sample_metadata(self):
        return self.deserialize_table(self.sample_metadata_bytes)

    @property
    def groups(self):
        return self.deserialize_table(self.groups_bytes)

    @property
    def measurements(self):
        measurement_metadata = self.measurement_metadata
        sample_metadata = self.sample_metadata
        table = self.raw_measurements
        table = normalize(self.normalization, table,
                          self.normalization_argument,
                          measurement_metadata,
                          sample_metadata)
        table = transform(self.transformation, table)
        table = scale(self.scaling, table)
        return table

    @property
    def table(self):
        """
        mimics the .table from the CSVFile but with validated data
        """
        return _generate_validated_table(self)


def _generate_validated_table(validated_table: ValidatedMetaboliteTable) -> pandas.DataFrame:
    # concat rows
    if not validated_table.measurement_metadata.empty:
        table = validated_table.measurement_metadata.copy()
        # normalize column names since R might have changed them
        table.columns = list(validated_table.measurements)
        table = table.append(validated_table.measurements, sort=False)
    else:
        table = validated_table.measurements.copy()

    # concat columns
    table = validated_table.groups.join(table, how='right')
    table = validated_table.sample_metadata.join(table, how='right')

    return table


class ValidatedMetaboliteTableSchema(BaseSchema):
    id = fields.UUID(missing=uuid4)
    created = fields.DateTime(dump_only=True)
    csv_file_id = fields.UUID(required=True)
    name = fields.Str(required=True)
    normalization = fields.Str(missing=None, validate=validate.OneOf(NORMALIZATION_METHODS))
    normalization_argument = fields.Str(missing=None)
    scaling = fields.Str(missing=None, validate=validate.OneOf(SCALING_METHODS))
    transformation = fields.Str(missing=None, validate=validate.OneOf(TRANSFORMATION_METHODS))
    meta = fields.Dict(missing=dict)
    imputation_info = fields.Dict(missing=dict)

    # not included in the serialized output
    raw_measurements_bytes = fields.Raw(required=True, load_only=True)
    measurement_metadata_bytes = fields.Raw(required=True, load_only=True)
    sample_metadata_bytes = fields.Raw(required=True, load_only=True)
    groups_bytes = fields.Raw(required=True, load_only=True)

    # tables stored in the database
    measurements = fields.Raw(required=True, dump_only=True)
    measurement_metadata = fields.Raw(required=True)
    sample_metadata = fields.Raw(required=True)
    groups = fields.Raw(required=True)

    # raw_measurements = fields.Raw(required=True, load_only=True) if needed in the future

    @post_dump
    def serialize_tables(self, data: Dict[str, Any], **kwargs):
        # don't transfer columns or index depending on the type
        def convert(attr, *drop_columns):
            if attr in data:
                converted = clean(data[attr]).to_dict(orient='split')
                for drop_column in drop_columns:
                    if drop_column in converted:
                        del converted[drop_column]
                data[attr] = converted

        convert('measurements', 'index', 'columns')
        convert('groups', 'index')
        convert('sample_metadata', 'index')
        convert('measurement_metadata', 'columns')

        return data

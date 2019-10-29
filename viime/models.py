from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path
import pickle
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, \
    Schema, validate, validates_schema
from marshmallow.exceptions import ValidationError
import numpy
import pandas
from sqlalchemy import MetaData
from sqlalchemy.event import listen
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename

from viime.cache import clear_cache, csv_file_cache, region
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
db = SQLAlchemy(metadata=metadata)

AxisNameTypes = namedtuple('AxisNameTypes', ['ROW', 'COLUMN'])
TableColumnTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK', 'GROUP'])
TableRowTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK'])
MetaDataTypes = namedtuple('MetaDataTypes', ['CATEGORICAL', 'NUMERICAL', 'ORDINAL'])
TABLE_COLUMN_TYPES = TableColumnTypes('key', 'metadata', 'measurement', 'masked', 'group')
TABLE_ROW_TYPES = TableRowTypes('header', 'metadata', 'sample', 'masked')
AXIS_NAME_TYPES = AxisNameTypes('row', 'column')
METADATA_TYPES = MetaDataTypes('categorical', 'numerical', 'ordinal')


def _guess_table_structure(table):
    # TODO: Implement this for real, this is just a dumb placeholder
    rows = [TABLE_ROW_TYPES.INDEX] + [
        TABLE_ROW_TYPES.DATA for i in range(table.shape[0] - 1)
    ]
    columns = [TABLE_COLUMN_TYPES.INDEX, TABLE_COLUMN_TYPES.GROUP] + [
        TABLE_COLUMN_TYPES.DATA for i in range(table.shape[1] - 2)
    ]
    return rows, columns


class BaseSchema(Schema):
    __model__ = None

    @post_load
    def make_object(self, data, **kwargs):
        if self.__model__ is not None:
            return self.__model__(**data)
        return data


class GroupLevel(db.Model):
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    name = db.Column(db.String, primary_key=True)
    color = db.Column(db.String, nullable=False)
    label = db.Column(db.String)
    description = db.Column(db.String)


class GroupLevelSchema(BaseSchema):
    __model__ = GroupLevel

    csv_file_id = fields.UUID(required=True, load_only=True)
    name = fields.Str(required=True)
    color = fields.Str(required=True)
    label = fields.Str()
    description = fields.Str(allow_none=True)


class CSVFile(db.Model):
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    imputation_mnar = db.Column(db.String, nullable=False)
    imputation_mcar = db.Column(db.String, nullable=False)
    meta = db.Column(JSONType, nullable=False)
    selected_columns = db.Column(db.PickleType, nullable=True)
    group_levels = relationship('GroupLevel', cascade='all, delete, delete-orphan')

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
        return _read_csv_file(self.uri, index_col=None, header=None)

    @property
    def indexed_table(self):
        return _indexed_table(self)

    @property
    def measurement_table(self):
        """Return the processed metabolite date table."""
        try:
            return _get_measurement_table(self)
        except Exception:
            current_app.logger.exception('Error getting measurement_table')
            raise

    @property
    def measurement_metadata(self):
        """Return metadata rows."""
        return _get_measurement_metadata(self)

    @property
    def sample_metadata(self):
        """Return metadata columns."""
        return _get_sample_metadata(self)

    @property
    def raw_measurement_table(self):
        """Return the metabolite data table before transformation."""
        return _get_raw_measurement_table(self)

    @property
    def groups(self):
        """Return a table containing the primary grouping column."""
        return _get_groups(self)

    @property
    def uri(self):
        id = str(self.id)
        return Path(current_app.config['UPLOAD_FOLDER']) / id[:3] / id

    @property
    def size(self):
        return Path(self.uri).stat().st_size

    @hybrid_property
    def header_row_index(self):
        return _header_row_index(self)

    @header_row_index.expression
    def header_row_index(cls):  # noqa: N805
        return TableRow.query\
            .filter_by(csv_file_id=cls.id, row_type=TABLE_ROW_TYPES.INDEX)\
            .with_entities(TableRow.row_index)\
            .scalar()

    @header_row_index.setter
    def header_row_index(self, value):
        if self.header_row_index is not None:
            old_row = self.rows[self.header_row_index]
            old_row.row_type = TABLE_ROW_TYPES.METADATA
            db.session.add(old_row)
            clear_cache()

        if value is not None:
            new_row = self.rows[value]
            new_row.row_type = TABLE_ROW_TYPES.INDEX
            db.session.add(new_row)
            clear_cache()

    @property
    def headers(self):
        return _headers(self)

    @hybrid_property
    def key_column_index(self):
        column = self.find_first_entity(
            lambda c: c.column_type == TABLE_COLUMN_TYPES.INDEX, self.columns)
        return column and column.column_index

    @key_column_index.expression
    def key_column_index(cls):  # noqa: N805
        return TableColumn.query\
            .filter_by(csv_file_id=cls.id, column_type=TABLE_COLUMN_TYPES.INDEX)\
            .with_entities(TableColumn.column_index)\
            .scalar()

    @key_column_index.setter
    def key_column_index(self, value):
        if self.key_column_index is not None:
            old_column = self.columns[self.key_column_index]
            old_column.column_type = TABLE_COLUMN_TYPES.METADATA
            db.session.add(old_column)
            clear_cache()

        if value is not None:
            new_column = self.columns[value]
            new_column.column_type = TABLE_COLUMN_TYPES.INDEX
            db.session.add(new_column)
            clear_cache()

    @hybrid_property
    def group_column_index(self):
        return _group_column_index(self)

    @group_column_index.expression
    def group_column_index(cls):  # noqa: N805
        return TableColumn.query\
            .filter_by(csv_file_id=cls.id, column_type=TABLE_COLUMN_TYPES.GROUP)\
            .with_entities(TableColumn.column_index)\
            .scalar()

    @group_column_index.setter
    def group_column_index(self, value):
        if self.group_column_index is not None:
            old_column = self.columns[self.group_column_index]
            old_column.column_type = TABLE_COLUMN_TYPES.METADATA
            db.session.add(old_column)
            clear_cache()
            self.group_levels = []

        if value is not None:
            new_column = self.columns[value]
            new_column.column_type = TABLE_COLUMN_TYPES.GROUP
            db.session.add(new_column)
            self.derive_group_levels()
            clear_cache()

    def derive_group_levels(self, clear_caches=False):
        if clear_caches:
            clear_cache(csv_file=self)
        groups = self.groups
        if groups is None or groups.empty:
            self.group_levels = []
            return
        levels = sorted([str(v) for v in groups.iloc[:, 0].unique()])
        # d3 scheme category 10
        colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
                  '#7f7f7f', '#bcbd22', '#17becf', '#ff7f0e']
        self.group_levels = [GroupLevel(name=l, label=l, color=colors[i % len(colors)])
                             for i, l in enumerate(levels)]

    @property
    def keys(self):
        return _keys(self)

    def filter_table_by_types(self, row_type, column_type):
        return _filter_table_by_types(self, row_type, column_type)

    @property
    def missing_cells(self):
        table = _coerce_numeric(self.raw_measurement_table)
        col, row = numpy.nonzero(table.isna().to_numpy())
        return numpy.column_stack((row, col)).astype(int).tolist()

    def apply_transforms(self):
        table = self.raw_measurement_table
        table = _coerce_numeric(table)
        table = impute_missing(
            table, self.groups, mnar=self.imputation_mnar, mcar=self.imputation_mcar)
        return table

    def save_table(self, table):
        # TODO: Delete cache entries if a file at self.uri exists already
        # For now, there is no API for changing the data contained in an uploaded
        # file, so this is not important.
        return self._save_csv_file_data(self.uri, table.to_csv())

    @property
    def _stats(self):
        return _get_csv_file_stats(self)

    @classmethod
    def create_csv_file(cls, id, name, table, **kwargs):
        csv_file = cls(id=id, name=name, **kwargs)
        cls._save_csv_file_data(csv_file.uri, table)
        row_types, column_types = _guess_table_structure(csv_file.table)

        rows = []
        table_row_schema = TableRowSchema()
        for index, row_type in enumerate(row_types):
            rows.append(table_row_schema.load({
                'csv_file_id': id, 'row_index': index, 'row_type': row_type
            }))

        csv_file.rows = rows

        columns = []
        table_column_schema = TableColumnSchema()
        for index, column_type in enumerate(column_types):
            columns.append(table_column_schema.load({
                'csv_file_id': id, 'column_index': index, 'column_type': column_type
            }))

        csv_file.columns = columns
        csv_file.derive_group_levels()

        return csv_file, rows, columns

    @classmethod
    def _save_csv_file_data(cls, uri, table_data):
        uri.parent.mkdir(parents=True, exist_ok=True)
        with open(uri, 'w') as f:
            f.write(table_data)
        clear_cache()
        return table_data

    def get_column_by_name(self, column_name):
        return self.find_first_entity(lambda c: c.column_header == column_name, self.columns)

    @classmethod
    def find_first_entity(cls, criterion, iterable):
        for entity in iterable:
            if criterion(entity):
                return entity
        return None


def _validate_table_data(table):
    try:
        pandas.read_csv(BytesIO(table.encode()))
    except Exception as e:
        raise ValidationError(str(e).strip(), data=table, field_name='table') from None


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

    columns = fields.List(fields.Nested('TableColumnSchema', exclude=['csv_file']))
    rows = fields.List(fields.Nested('TableRowSchema', exclude=['csv_file']))

    selected_columns = fields.List(fields.Str(), dump_only=True, missing=list)
    group_levels = fields.List(fields.Nested('GroupLevelSchema'))

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
            data['measurement_table'] = data['measurement_table'].to_dict(
                orient='split')
        return data

    @post_load
    def make_object(self, data, **kwargs):
        csv_file, rows, columns = CSVFile.create_csv_file(**data)
        db.session.add(csv_file)
        db.session.add_all(rows + columns)
        return csv_file


class TableColumn(db.Model):
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    column_index = db.Column(db.Integer, primary_key=True)
    column_type = db.Column(db.String, nullable=False)
    subtype = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=True)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('columns', lazy=True, order_by='TableColumn.column_index'))

    @property
    def data_column_index(self):
        return _data_column_index(self)

    @property
    def column_header(self):
        return self.csv_file.headers[self.column_index]

    @property
    def missing_percent(self):
        if self.column_type == TABLE_COLUMN_TYPES.DATA:
            return self.csv_file._stats and \
                self.csv_file._stats['columns']['missing'][self.data_column_index]

    @property
    def data_variance(self):
        if self.column_type == TABLE_COLUMN_TYPES.DATA:
            return self.csv_file._stats and \
                self.csv_file._stats['columns']['variance'][self.data_column_index]


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn

    csv_file_id = fields.UUID(required=True, load_only=True)
    column_header = fields.Str(dump_only=True)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    subtype = fields.Str(required=False, validate=validate.OneOf(METADATA_TYPES))
    meta = fields.Dict(missing=dict)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns'], dump_only=True)


class TableRow(db.Model):
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    row_type = db.Column(db.String, nullable=False)
    subtype = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=True)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('rows', lazy=True, order_by='TableRow.row_index'))

    @property
    def row_name(self):
        return self.csv_file.keys[self.row_index]

    @property
    def data_row_index(self):
        return _data_row_index(self)

    @property
    def missing_percent(self):
        if self.row_type == TABLE_ROW_TYPES.DATA:
            return self.csv_file._stats['rows']['missing'][self.data_row_index]

    @property
    def data_variance(self):
        if self.row_type == TABLE_ROW_TYPES.DATA:
            return self.csv_file._stats['rows']['variance'][self.data_row_index]


class TableRowSchema(BaseSchema):
    __model__ = TableRow

    csv_file_id = fields.UUID(required=True, load_only=True)
    row_name = fields.Str(dump_only=True)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    subtype = fields.Str(required=False, validate=validate.OneOf(METADATA_TYPES))
    meta = fields.Dict(missing=dict)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns'], dump_only=True)


class ModifyLabelChangesSchema(Schema):
    context = fields.Str(required=True, validate=validate.OneOf(AXIS_NAME_TYPES))
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


listen(CSVFile, 'after_update', lambda mapper, connection, target: clear_cache(csv_file=target))
listen(TableRow, 'after_update',
       lambda mapper, connection, target: clear_cache(csv_file=target.csv_file))
listen(TableColumn, 'after_update',
       lambda mapper, connection, target: clear_cache(csv_file=target.csv_file))


# Cached class method implementations:
# These are placed here because dogpile does not allow you
# to include the class instance in the cache key.  :'(
@region.cache_on_arguments()
def _read_csv_file(path, **kwargs):
    return pandas.read_csv(path, **kwargs)


@region.cache_on_arguments()
def _header_row_index(csv_file):
    row = csv_file.find_first_entity(lambda r: r.row_type == TABLE_ROW_TYPES.INDEX, csv_file.rows)
    return row and row.row_index


@region.cache_on_arguments()
def _headers(csv_file):
    idx = csv_file.header_row_index
    if idx is None:
        return [
            f'col{i + 1}' for i in range(csv_file.table.shape[1])
        ]

    return list(csv_file.table.iloc[idx, :])


@region.cache_on_arguments()
def _group_column_index(csv_file):
    column = csv_file.find_first_entity(
        lambda c: c.column_type == TABLE_COLUMN_TYPES.GROUP, csv_file.columns)
    return column and column.column_index


@region.cache_on_arguments()
def _keys(csv_file):
    idx = csv_file.key_column_index
    if idx is None:
        return [
            f'row{i + 1}' for i in range(csv_file.table.shape[0])
        ]

    return list(csv_file.table.iloc[:, idx])


@region.cache_on_arguments()
def _get_table_stats(table):
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


@region.cache_on_arguments()
def _filter_table_by_types(csv_file, row_type, column_type):
    if csv_file.header_row_index is None or \
            csv_file.key_column_index is None:
        return
    rows = [
        row.row_index for row in csv_file.rows
        if row.row_type == row_type
    ]
    if csv_file.header_row_index is not None:
        rows = [csv_file.header_row_index] + rows
    else:
        current_app.logger.warning('No header row is set.')

    columns = [
        column.column_index for column in csv_file.columns
        if column.column_type == column_type
    ]
    if csv_file.key_column_index is not None:
        index_col = 0
        columns = [csv_file.key_column_index] + columns
    else:
        index_col = None

    return pandas.read_csv(
        BytesIO(
            csv_file.table.iloc[rows, columns].to_csv(header=False, index=False).encode()
        ), index_col=index_col
    )


@region.cache_on_arguments()
def _indexed_table(csv_file):
    kwargs = {}

    # handle column names
    header_row = csv_file.header_row_index
    kwargs['header'] = header_row
    if header_row is None:
        kwargs['names'] = csv_file.headers

    # handle row ids
    kwargs['index_col'] = False
    key_column = csv_file.key_column_index
    if key_column is not None:
        kwargs['index_col'] = key_column

    indexed_table = _read_csv_file(csv_file.uri, **kwargs)

    # inject the computed keys in case the csv file does not have a primary key column
    if key_column is None:
        keys = csv_file.keys

        # exclude the header row from the primary key index if present
        if header_row is not None:
            keys = keys[1:]
        indexed_table.index = pandas.Index(keys)

    return indexed_table


@region.cache_on_arguments()
def _data_row_index(row):
    """Return the index in the measurement table or None if not a data row."""
    if row.row_type != TABLE_ROW_TYPES.DATA:
        return None
    query = row.query.filter_by(csv_file_id=row.csv_file_id, row_type=TABLE_ROW_TYPES.DATA)
    return query.filter(TableRow.row_index < row.row_index).count()


@region.cache_on_arguments()
def _data_column_index(column):
    """Return the index in the measurement table or None if not a data column."""
    if column.column_type != TABLE_COLUMN_TYPES.DATA:
        return None
    query = column.query.filter_by(
        csv_file_id=column.csv_file_id, column_type=TABLE_COLUMN_TYPES.DATA)
    return query.filter(TableColumn.column_index < column.column_index).count()


@region.cache_on_arguments()
def _coerce_numeric(table):
    """Coerce a table into numeric values."""
    for i in range(table.shape[1]):
        table.iloc[:, i] = pandas.to_numeric(table.iloc[:, i], errors='coerce')
    return table


# The following methods are stored in a persistent cache (memcached) if configured.
# They are for more complicated functions that could take significant time to execute
# and are commonly called between multiple rest endpoints with the same value.
@csv_file_cache
def _get_raw_measurement_table(csv_file):
    return csv_file.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.DATA)


@csv_file_cache
def _get_measurement_table(csv_file):
    if not get_fatal_index_errors(csv_file):
        try:
            return csv_file.apply_transforms()
        except Exception as e:
            # TODO: We should handle this better
            current_app.logger.exception(e)


@csv_file_cache
def _get_measurement_metadata(csv_file):
    return csv_file.filter_table_by_types(TABLE_ROW_TYPES.METADATA, TABLE_COLUMN_TYPES.DATA)


@csv_file_cache
def _get_sample_metadata(csv_file):
    return csv_file.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.METADATA)


@csv_file_cache
def _get_groups(csv_file):
    if csv_file.group_column_index is None:
        return None
    return csv_file.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.GROUP)


@csv_file_cache
def _get_csv_file_stats(csv_file):
    if csv_file.raw_measurement_table is not None:
        return _get_table_stats(csv_file.raw_measurement_table)


class ValidatedMetaboliteTable(db.Model):
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), nullable=False,
                            index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    normalization = db.Column(db.String, nullable=True)
    normalization_argument = db.Column(db.String, nullable=True)
    transformation = db.Column(db.String, nullable=True)
    scaling = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=False)

    raw_measurements_bytes = db.Column(db.LargeBinary, nullable=False)
    measurement_metadata_bytes = db.Column(db.LargeBinary, nullable=False)
    sample_metadata_bytes = db.Column(db.LargeBinary, nullable=False)
    groups_bytes = db.Column(db.LargeBinary, nullable=False)

    @classmethod
    def serialize_table(cls, table):
        return pickle.dumps(table)

    @classmethod
    def deserialize_table(cls, blob):
        return pickle.loads(blob)

    @classmethod
    def create_from_csv_file(cls, csv_file, **kwargs):
        table = csv_file.measurement_table
        assert table is not None, 'Invalid csv_file provided'

        attributes = {
            'id': uuid4(),
            'csv_file_id': csv_file.id,
            'name': csv_file.name,
            'meta': csv_file.meta.copy(),
            'raw_measurements_bytes': cls.serialize_table(table),
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


def _generate_validated_table(validated_table):
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
    def serialize_tables(self, data, **kwargs):
        # don't transfer columns or index depending on the type
        def convert(attr, *drop_columns):
            if attr in data:
                converted = data[attr].to_dict(orient='split')
                for drop_column in drop_columns:
                    if drop_column in converted:
                        del converted[drop_column]
                data[attr] = converted

        convert('measurements', 'index', 'columns')
        convert('groups', 'index')
        convert('sample_metadata', 'index')
        convert('measurement_metadata', 'columns')

        return data

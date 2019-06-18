from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePath
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, \
    Schema, validate, validates_schema
from marshmallow.exceptions import ValidationError
import pandas
from sqlalchemy import MetaData, UniqueConstraint
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename

from metabulo.cache import clear_cache, csv_file_cache, region
from metabulo.imputation import IMPUTE_MCAR_METHODS, impute_missing, IMPUTE_MNAR_METHODS
from metabulo.normalization import NORMALIZATION_METHODS, normalize
from metabulo.scaling import scale, SCALING_METHODS
from metabulo.table_validation import get_fatal_index_errors, get_validation_list
from metabulo.transformation import transform, TRANSFORMATION_METHODS

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
TABLE_COLUMN_TYPES = TableColumnTypes('key', 'metadata', 'measurement', 'masked', 'group')
TABLE_ROW_TYPES = TableRowTypes('header', 'metadata', 'sample', 'masked')
AXIS_NAME_TYPES = AxisNameTypes('row', 'column')


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
    def make_object(self, data):
        if self.__model__ is not None:
            return self.__model__(**data)
        return data


class CSVFile(db.Model):
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    imputation_mnar = db.Column(db.String, nullable=False)
    imputation_mcar = db.Column(db.String, nullable=False)
    normalization = db.Column(db.String, nullable=True)
    transformation = db.Column(db.String, nullable=True)
    scaling = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=False)

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
    def header_row(self):
        return TableRow.query.filter_by(
            csv_file_id=self.id,
            row_type=TABLE_ROW_TYPES.INDEX
        ).first()

    @property
    def key_column(self):
        return TableColumn.query.filter_by(
            csv_file_id=self.id,
            column_type=TABLE_COLUMN_TYPES.INDEX
        ).first()

    @property
    def group_column(self):
        return TableColumn.query.filter_by(
            csv_file_id=self.id,
            column_type=TABLE_COLUMN_TYPES.GROUP
        ).first()

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

    @property
    def headers(self):
        return [c.column_header for c in self.columns]

    @property
    def keys(self):
        return [r.row_name for r in self.rows]

    def filter_table_by_types(self, row_type, column_type):
        return _filter_table_by_types(self, row_type, column_type)

    def apply_transforms(self):
        table = self.raw_measurement_table
        table = _coerce_numeric(table)
        table = impute_missing(
            table, self.groups, mnar=self.imputation_mnar, mcar=self.imputation_mcar)
        table = normalize(self.normalization, table)
        table = transform(self.transformation, table)
        table = scale(self.scaling, table)
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

        columns = []
        table_column_schema = TableColumnSchema()
        for index, column_type in enumerate(column_types):
            columns.append(table_column_schema.load({
                'csv_file_id': id, 'column_index': index, 'column_type': column_type
            }))

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


def _validate_name(name):
    if PurePath(name).suffix != '.csv':
        raise ValidationError('Only CSV files are allowed', data=name, field_name='name')


class CSVFileSchema(BaseSchema):
    id = fields.UUID(missing=uuid4)
    created = fields.DateTime(dump_only=True)
    name = fields.Str(required=True, validate=_validate_name)
    table = fields.Raw(required=True, validate=_validate_table_data)
    imputation_mnar = fields.Str(missing='zero', validate=validate.OneOf(IMPUTE_MNAR_METHODS))
    imputation_mcar = fields.Str(
        missing='random-forest', validate=validate.OneOf(IMPUTE_MCAR_METHODS))
    normalization = fields.Str(missing=None, validate=validate.OneOf(NORMALIZATION_METHODS))
    transformation = fields.Str(missing=None, validate=validate.OneOf(TRANSFORMATION_METHODS))
    scaling = fields.Str(missing=None, validate=validate.OneOf(SCALING_METHODS))
    meta = fields.Dict(missing=dict)

    columns = fields.List(fields.Nested('TableColumnSchema', exclude=['csv_file']))
    rows = fields.List(fields.Nested('TableRowSchema', exclude=['csv_file']))

    table_validation = fields.Nested('ValidationSchema', many=True, dump_only=True)
    measurement_table = fields.Raw(dump_only=True, allow_none=True)
    measurement_metadata = fields.Raw(dump_only=True, allow_none=True)
    sample_metadata = fields.Raw(dump_only=True, allow_none=True)
    groups = fields.Raw(dump_only=True, allow_none=True)
    size = fields.Int(dump_only=True)

    @post_load
    def fix_file_name(self, data):
        data['name'] = secure_filename(data['name'])
        return data

    @post_dump
    def read_csv_file(self, data):
        def get_csv(key):
            if data.get(key) is not None:
                return data[key].to_csv()

        data['table'] = data['table'].to_csv(header=False, index=False)
        data['measurement_table'] = get_csv('measurement_table')
        data['measurement_metadata'] = get_csv('measurement_metadata')
        data['sample_metadata'] = get_csv('sample_metadata')
        data['groups'] = get_csv('groups')
        return data

    @post_load
    def make_object(self, data):
        csv_file, rows, columns = CSVFile.create_csv_file(**data)
        db.session.add(csv_file)
        db.session.add_all(rows + columns)

        from metabulo.triggers import after_create_csv_file
        after_create_csv_file(csv_file)

        return csv_file


class TableColumn(db.Model):
    __table_args__ = (
        UniqueConstraint('column_index', 'csv_file_id'),
        UniqueConstraint('data_column_index', 'csv_file_id')
    )

    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    column_index = db.Column(db.Integer, primary_key=True)
    column_type = db.Column(db.String, nullable=False)
    column_header = db.Column(db.String, nullable=True)  # nullable
    data_column_index = db.Column(db.Integer, nullable=True)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('columns', lazy=True, order_by='TableColumn.column_index'),
        lazy=True)

    @property
    def missing_percent(self):
        if self.column_type == TABLE_COLUMN_TYPES.DATA:
            return self.csv_file._stats and \
                self.csv_file._stats['columns']['missing'][self.data_column.column_index]

    @property
    def data_variance(self):
        if self.column_type == TABLE_COLUMN_TYPES.DATA:
            return self.csv_file._stats and \
                self.csv_file._stats['columns']['variance'][self.data_column.column_index]


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn

    csv_file_id = fields.UUID(required=True, load_only=True)
    column_header = fields.Str(default=None)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    data_column_index = fields.Int(default=None)

    missing_percent = fields.Float(dump_only=True, allow_none=True)
    data_variance = fields.Float(dump_only=True, allow_none=True, allow_nan=True)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'table'], dump_only=True)

    @post_dump
    def coerce_nan(self, data):
        data.setdefault('data_variance', None)
        if data['data_variance'] != data['data_variance']:
            data['data_variance'] = None
        return data


class TableRow(db.Model):
    __table_args__ = (
        UniqueConstraint('row_index', 'csv_file_id'),
        UniqueConstraint('data_row_index', 'csv_file_id')
    )

    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    row_type = db.Column(db.String, nullable=False)
    row_name = db.Column(db.String, nullable=True)  # nullable
    data_row_index = db.Column(db.Integer, nullable=True)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('rows', lazy=True, order_by='TableRow.row_index'),
        lazy=True)

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
    row_name = fields.Str(default=None)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    data_row_index = fields.Int(default=None)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns'], dump_only=True)


class ModifyLabelChangesSchema(Schema):
    context = fields.Str(required=True, validate=validate.OneOf(AXIS_NAME_TYPES))
    index = fields.Int(required=True, validate=validate.Range(min=0))
    label = fields.Str(required=True)

    @validates_schema
    def validate_label(self, data):
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


# Cached class method implementations:
# These are placed here because dogpile does not allow you
# to include the class instance in the cache key.  :'(
@region.cache_on_arguments()
def _read_csv_file(path, **kwargs):
    return pandas.read_csv(path, **kwargs)


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
    header_row = csv_file.header_row
    key_column = csv_file.key_column

    if header_row is None or key_column is None:
        return

    rows = [header_row.row_index]
    rows += [
        row.row_index for row in csv_file.rows
        if row.row_type == row_type
    ]

    columns = [key_column.column_index]
    columns += [
        column.column_index for column in csv_file.columns
        if column.column_type == column_type
    ]

    return pandas.read_csv(
        BytesIO(
            csv_file.table.iloc[rows, columns].to_csv(header=False, index=False).encode()
        ), index_col=0
    )


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
    if csv_file.group_column is None:
        return None
    return csv_file.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.GROUP)


@csv_file_cache
def _get_csv_file_stats(csv_file):
    table = csv_file.raw_measurement_table
    if table is not None:
        return _get_table_stats(table)

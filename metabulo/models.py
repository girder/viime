from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePath
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, pre_load, Schema, validate
from marshmallow.exceptions import ValidationError
import pandas
from sqlalchemy import MetaData
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename

from metabulo.cache import clear_cache, region
from metabulo.imputation import impute_missing
from metabulo.normalization import NORMALIZATION_METHODS, normalize


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

TableColumnTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK', 'GROUP'])
TableRowTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK'])
TABLE_COLUMN_TYPES = TableColumnTypes('key', 'metadata', 'measurement', 'masked', 'group')
TABLE_ROW_TYPES = TableRowTypes('header', 'metadata', 'sample', 'masked')


def _guess_table_structure(table):
    # TODO: Implement this for real, this is just a dumb placeholder
    rows = [TABLE_ROW_TYPES.INDEX] + [
        TABLE_ROW_TYPES.DATA for i in range(table.shape[0] - 1)
    ]
    columns = [TABLE_COLUMN_TYPES.INDEX, TABLE_COLUMN_TYPES.GROUP] + [
        TABLE_COLUMN_TYPES.DATA for i in range(table.shape[1] - 2)
    ]
    return rows, columns


@region.cache_on_arguments()
def _read_csv_file(path, **kwargs):
    return pandas.read_csv(path, **kwargs)


@region.cache_on_arguments()
def _get_table_stats(table):
    # Get global stats all once because it is more efficient than
    # doing it per row/column.
    nan_table = table != table
    return {
        'columns': {
            'missing': (nan_table.sum(axis=0) / nan_table.shape[0]).to_list(),
            'variance': table.var(axis=0).to_list()
        },
        'rows': {
            'missing': (nan_table.sum(axis=1) / nan_table.shape[1]).to_list(),
            'variance': table.var(axis=1).to_list()
        }
    }


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
    normalization = db.Column(db.String, nullable=True)
    meta = db.Column(JSONType, nullable=False)

    @property
    @region.cache_on_arguments()
    def table_validation(self):
        """Return a list of issues with the table or None if everything is okay."""
        errors = []
        if self.header_row_index is None:
            errors.append('No header row')
        if self.key_column_index is None:
            errors.append('No primary key column')
        if self.group_column_index is None:
            errors.append('No group column')

        if not errors:
            try:
                self.apply_transforms()
            except Exception:
                errors.append('Error applying transforms')

        return errors or None

    @property
    @region.cache_on_arguments()
    def table(self):
        return _read_csv_file(self.uri, index_col=None, header=None)

    @property
    @region.cache_on_arguments()
    def indexed_table(self):
        kwargs = {}

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

        indexed_table = _read_csv_file(self.uri, **kwargs)

        # inject the computed keys in case the csv file does not have a primary key column
        if key_column is None:
            keys = self.keys

            # exclude the header row from the primary key index if present
            if header_row is not None:
                keys = keys[1:]
            indexed_table.index = pandas.Index(keys)

        return indexed_table

    @property
    @region.cache_on_arguments()
    def measurement_table(self):
        """Return the processed metabolite date table."""
        if self.table_validation is None:
            return self.apply_transforms()

    @property
    @region.cache_on_arguments()
    def measurement_metadata(self):
        """Return metadata rows."""
        return self.filter_table_by_types(TABLE_ROW_TYPES.METADATA, TABLE_COLUMN_TYPES.DATA)

    @property
    @region.cache_on_arguments()
    def sample_metadata(self):
        """Return metadata columns."""
        return self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.METADATA)

    @property
    @region.cache_on_arguments()
    def raw_measurement_table(self):
        """Return the metabolite data table before transformation."""
        return self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.DATA)

    @property
    @region.cache_on_arguments()
    def groups(self):
        """Return a table containing the primary grouping column."""
        if self.group_column_index is None:
            return None
        return self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.GROUP)

    @property
    def uri(self):
        id = str(self.id)
        return Path(current_app.config['UPLOAD_FOLDER']) / id[:3] / id

    @hybrid_property
    def header_row_index(self):
        row = self.find_first_entity(lambda r: r.row_type == TABLE_ROW_TYPES.INDEX, self.rows)
        return row and row.row_index

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
    @region.cache_on_arguments()
    def headers(self):
        idx = self.header_row_index
        if idx is None:
            return [
                f'col{i + 1}' for i in range(self.table.shape[1])
            ]

        return list(self.table.iloc[idx, :])

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
        column = self.find_first_entity(
            lambda c: c.column_type == TABLE_COLUMN_TYPES.GROUP, self.columns)
        return column and column.column_index

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

        if value is not None:
            new_column = self.columns[value]
            new_column.column_type = TABLE_COLUMN_TYPES.GROUP
            db.session.add(new_column)
            clear_cache()

    @property
    @region.cache_on_arguments()
    def keys(self):
        idx = self.key_column_index
        if idx is None:
            return [
                f'row{i + 1}' for i in range(self.table.shape[0])
            ]

        return list(self.table.iloc[:, idx])

    @region.cache_on_arguments()
    def filter_table_by_types(self, row_type, column_type):
        if self.header_row_index is None or \
                self.key_column_index is None:
            return
        rows = [
            row.row_index for row in self.rows
            if row.row_type == row_type
        ]
        if self.header_row_index is not None:
            rows = [self.header_row_index] + rows
        else:
            current_app.logger.warning('No header row is set.')

        columns = [
            column.column_index for column in self.columns
            if column.column_type == column_type
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

    @region.cache_on_arguments()
    def apply_transforms(self):
        table = self.raw_measurement_table
        table = impute_missing(table, self.groups)
        return normalize(self.normalization, table)

    def save_table(self, table):
        # TODO: Delete cache entries if a file at self.uri exists already
        # For now, there is no API for changing the data contained in an uploaded
        # file, so this is not important.
        return self._save_csv_file_data(self.uri, table.to_csv())

    @property
    def _stats(self):
        return _get_table_stats(self.raw_measurement_table)

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
    normalization = fields.Str(missing=None, validate=validate.OneOf(NORMALIZATION_METHODS))
    meta = fields.Dict(missing=dict)

    columns = fields.List(fields.Nested('TableColumnSchema', exclude=['csv_file']))
    rows = fields.List(fields.Nested('TableRowSchema', exclude=['csv_file']))

    table_validation = fields.List(fields.Str, dump_only=True, allow_none=True)
    measurement_table = fields.Raw(dump_only=True, allow_none=True)
    measurement_metadata = fields.Raw(dump_only=True, allow_none=True)
    sample_metadata = fields.Raw(dump_only=True, allow_none=True)
    groups = fields.Raw(dump_only=True, allow_none=True)

    _stats = fields.Raw(dump_only=True)

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
        return csv_file


class TableColumn(db.Model):
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    column_index = db.Column(db.Integer, primary_key=True)
    column_type = db.Column(db.String, nullable=False)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('columns', lazy=True, order_by='TableColumn.column_index'))

    @property
    @region.cache_on_arguments()
    def data_column_index(self):
        """Return the index in the measurement table or None if not a data column."""
        if self.column_type != TABLE_COLUMN_TYPES.DATA:
            return None
        query = self.query.filter_by(
            csv_file_id=self.csv_file_id, column_type=TABLE_COLUMN_TYPES.DATA)
        return query.filter(TableColumn.column_index < self.column_index).count()

    @property
    @region.cache_on_arguments()
    def column_header(self):
        return self.csv_file.headers[self.column_index]

    @property
    @region.cache_on_arguments(namespace='TableColumn')
    def missing_percent(self):
        if self.column_type == TABLE_COLUMN_TYPES.DATA:
            return self.csv_file._stats['columns']['missing'][self.data_column_index]

    @property
    @region.cache_on_arguments(namespace='TableColumn')
    def data_variance(self):
        if self.column_type == TABLE_COLUMN_TYPES.DATA:
            return self.csv_file._stats['columns']['variance'][self.data_column_index]


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn

    csv_file_id = fields.UUID(required=True, load_only=True)
    column_header = fields.Str(dump_only=True)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    data_column_index = fields.Int(dump_only=True, allow_none=True)

    missing_percent = fields.Float(dump_only=True, allow_none=True)
    data_variance = fields.Float(dump_only=True, allow_none=True)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns'], dump_only=True)


class ModifyColumnSchema(Schema):
    column_type = fields.Str(required=False, validate=validate.OneOf(TABLE_COLUMN_TYPES))

    @pre_load
    def validate_not_empty(self, data):
        if data is None or data == {}:
            raise ValidationError('JSON params required', data=data)
        return data


class TableRow(db.Model):
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    row_type = db.Column(db.String, nullable=False)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('rows', lazy=True, order_by='TableRow.row_index'))

    @property
    @region.cache_on_arguments()
    def row_name(self):
        return self.csv_file.keys[self.row_index]

    @property
    @region.cache_on_arguments()
    def data_row_index(self):
        """Return the index in the measurement table or None if not a data row."""
        if self.row_type != TABLE_ROW_TYPES.DATA:
            return None
        query = self.query.filter_by(csv_file_id=self.csv_file_id, row_type=TABLE_ROW_TYPES.DATA)
        return query.filter(TableRow.row_index < self.row_index).count()

    @property
    @region.cache_on_arguments(namespace='TableRow')
    def missing_percent(self):
        if self.row_type == TABLE_ROW_TYPES.DATA:
            return self.csv_file._stats['rows']['missing'][self.data_row_index]

    @property
    @region.cache_on_arguments(namespace='TableRow')
    def data_variance(self):
        if self.row_type == TABLE_ROW_TYPES.DATA:
            return self.csv_file._stats['rows']['variance'][self.data_row_index]


class TableRowSchema(BaseSchema):
    __model__ = TableRow

    csv_file_id = fields.UUID(required=True, load_only=True)
    row_name = fields.Str(dump_only=True)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    data_row_index = fields.Int(dump_only=True, allow_none=True)

    missing_percent = fields.Float(dump_only=True, allow_none=True)
    data_variance = fields.Float(dump_only=True, allow_none=True)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns'], dump_only=True)


class ModifyRowSchema(Schema):
    row_type = fields.Str(required=False, validate=validate.OneOf(TABLE_ROW_TYPES))

    @pre_load
    def validate_not_empty(self, data):
        if data is None or data == {}:
            raise ValidationError('JSON params required', data=data)
        return data

from collections import namedtuple
from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePath
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, pre_load, Schema, validate
from marshmallow.exceptions import ValidationError
import numpy as np
import pandas
from sqlalchemy import MetaData
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename

from metabulo import transform


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

TableTypes = namedtuple('TableTypes', ['INDEX', 'METADATA', 'DATA', 'MASK'])
TABLE_COLUMN_TYPES = TableTypes('key', 'metadata', 'measurement', 'masked')
TABLE_ROW_TYPES = TableTypes('header', 'metadata', 'sample', 'masked')


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
    meta = db.Column(JSONType, nullable=False)

    @property
    def raw_table(self):
        if not hasattr(self, '_raw_table'):
            self._raw_table = pandas.read_csv(self.uri, index_col=None, header=None)
        return self._raw_table.copy()

    @property
    def table(self):
        if not hasattr(self, '_table'):
            self._table = pandas.read_csv(self.uri, index_col=0)
        return self._table.copy()

    @property
    def measurement_table(self):
        return self.apply_transforms()

    @property
    def measurement_metadata(self):
        return self.filter_table_by_types(TABLE_ROW_TYPES.METADATA, TABLE_COLUMN_TYPES.DATA)

    @property
    def sample_metadata(self):
        return self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.METADATA)

    @property
    def transforms(self):
        query = TableTransform.query.filter_by(csv_file_id=self.id)
        return query.order_by(TableTransform.priority)

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

    @property
    def headers(self):
        idx = self.header_row_index
        # TODO:
        assert idx is not None, 'Tables without headers are not supported'

        return list(self.raw_table.iloc[idx, :])

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

    @property
    def keys(self):
        idx = self.key_column_index
        # TODO:
        assert idx is not None, 'Tables without primary keys are not supported'

        return list(self.raw_table.iloc[:, idx])

    def filter_table_by_types(self, row_type, column_type):
        rows = [
            row.row_index - 1 for row in self.rows
            if row.row_type in (row_type,)
        ]
        columns = [
            column.column_index - 1 for column in self.columns
            if column.column_type in (column_type,)
        ]
        return self.table.iloc[rows, columns]

    def apply_transforms(self, last=None):
        table = self.filter_table_by_types(TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.DATA)
        for t in self.transforms:
            table = t.apply(table)
            if str(t.id) == str(last):
                break
        return table

    def generate_transform(self, data):
        args = data.copy()
        transform_type = args.pop('transform_type', None)
        priority = args.pop('priority', None)
        data = {
            'csv_file_id': str(self.id),
            'transform_type': transform_type,
            'args': args,
            'priority': priority
        }
        schema = TableTransformSchema()
        return schema.load(data)

    def save_table(self, table):
        if hasattr(self, '_raw_table'):
            del self._raw_table
        if hasattr(self, '_table'):
            del self._table
        return self._save_csv_file_data(self.uri, table.to_csv())

    def _generate_table_columns(self):
        table_column_schema = TableColumnSchema()
        table = self.table

        columns = []
        if table.index is None:
            raise ValidationError('No primary key column detected')

        index = 0
        columns.append(
            table_column_schema.load({
                'csv_file_id': self.id,
                'column_index': index,
                'column_type': TABLE_COLUMN_TYPES.INDEX,
            })
        )
        index += 1
        for column_header, dtype in table.dtypes.items():
            # There are probably better heuristics for this.
            if dtype == np.object:
                column_type = TABLE_COLUMN_TYPES.METADATA
            else:
                column_type = TABLE_COLUMN_TYPES.DATA

            columns.append(
                table_column_schema.load({
                    'csv_file_id': self.id,
                    'column_index': index,
                    'column_type': column_type,
                })
            )
            index += 1
        return columns

    def _generate_table_rows(self):
        table_row_schema = TableRowSchema()
        table = self.table

        # Assuming the first row contains the header for the table.  Removing this assumption
        # would probably mean reading the table by something other than pandas.read_csv.
        rows = [
            table_row_schema.load({
                'csv_file_id': self.id,
                'row_index': 0,
                'row_type': TABLE_ROW_TYPES.INDEX,
            })
        ]

        # Assume all other rows are samples.  There may be other heuristics
        # to apply here in the future.  Or maybe mask rows with too many
        # NaN's.
        for index, row_name in enumerate(table.index):
            rows.append(
                table_row_schema.load({
                    'csv_file_id': self.id,
                    'row_index': index + 1,
                    'row_type': TABLE_ROW_TYPES.DATA,
                })
            )
        return rows

    @classmethod
    def create_csv_file(cls, id, name, table, meta=None):
        csv_file = cls(id=id, name=name, meta=meta)
        cls._save_csv_file_data(csv_file.uri, table)
        rows = csv_file._generate_table_rows()
        columns = csv_file._generate_table_columns()
        return csv_file, rows, columns

    @classmethod
    def _save_csv_file_data(cls, uri, table_data):
        uri.parent.mkdir(parents=True, exist_ok=True)
        with open(uri, 'w') as f:
            f.write(table_data)
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
    meta = fields.Dict(missing=dict)

    columns = fields.List(fields.Nested('TableColumnSchema', exclude=['csv_file']))
    rows = fields.List(fields.Nested('TableRowSchema', exclude=['csv_file']))
    transforms = fields.List(
        fields.Nested('TableTransformSchema', exclude=['csv_file']), dump_only=True)

    measurement_table = fields.Raw(dump_only=True)
    measurement_metadata = fields.Raw(dump_only=True)
    sample_metadata = fields.Raw(dump_only=True)

    @post_load
    def fix_file_name(self, data):
        data['name'] = secure_filename(data['name'])
        return data

    @post_dump
    def read_csv_file(self, data):
        data['table'] = data['table'].to_csv()
        data['measurement_table'] = data['measurement_table'].to_csv()
        data['measurement_metadata'] = data['measurement_metadata'].to_csv()
        data['sample_metadata'] = data['sample_metadata'].to_csv()
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
    def column_header(self):
        return self.csv_file.headers[self.column_index]


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn

    csv_file_id = fields.UUID(required=True, load_only=True)
    column_header = fields.Str(dump_only=True)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'transforms'], dump_only=True)


class ModifyColumnSchema(Schema):
    column_type = fields.Str(required=False, validate=validate.OneOf(TABLE_COLUMN_TYPES))

    @pre_load
    def validate_not_empty(self, data):
        if data is None or data == {}:
            raise ValidationError('JSON params required', data=data)
        return data

    @post_load
    def validate_type(self, data):
        if data.get('column_type') == 'key':
            raise ValidationError(
                'Setting the key not yet supported', data='key', field_name='column_type')
        return data


class TableRow(db.Model):
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    row_type = db.Column(db.String, nullable=False)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('rows', lazy=True, order_by='TableRow.row_index'))

    @property
    def row_name(self):
        return self.csv_file.keys[self.row_index]


class TableRowSchema(BaseSchema):
    __model__ = TableRow

    csv_file_id = fields.UUID(required=True, load_only=True)
    row_name = fields.Str(dump_only=True)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'transforms'], dump_only=True)


class ModifyRowSchema(Schema):
    row_type = fields.Str(required=False, validate=validate.OneOf(TABLE_ROW_TYPES))

    @pre_load
    def validate_not_empty(self, data):
        if data is None or data == {}:
            raise ValidationError('JSON params required', data=data)
        return data

    @post_load
    def validate_type(self, data):
        if data.get('row_type') == TABLE_ROW_TYPES.INDEX:
            raise ValidationError(
                'Setting row primary key not yet supported',
                data=data.get('row_type'), field_name='row_type')
        return data


class TableTransform(db.Model):
    __table_args__ = (UniqueConstraint('id', 'priority'),)

    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transform_type = db.Column(db.String, nullable=False)
    args = db.Column(JSONType, nullable=False)
    priority = db.Column(db.Float, nullable=False)

    csv_file = db.relationship(CSVFile)

    def apply(self, table):
        kwargs = dict(
            table=table,
            transform_type=self.transform_type,
            **self.args
        )
        return transform.dispatch(**kwargs)


class TableTransformSchema(BaseSchema):
    __model__ = TableTransform

    id = fields.UUID(missing=uuid4)
    csv_file_id = fields.UUID(required=True, load_only=True)
    created = fields.DateTime(dump_only=True)
    transform_type = fields.Str(required=True, validate=validate.OneOf(transform.registry.keys()))
    args = fields.Dict(missing=dict)
    priority = fields.Float(required=True)

    csv_file = fields.Nested(CSVFileSchema, exclude=['transforms'], dump_only=True)

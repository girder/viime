from collections import namedtuple
from datetime import datetime
from io import BytesIO
from math import isnan, floor
from pathlib import Path, PurePath
from typing import Iterable
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, pre_load, Schema, validate
from marshmallow.exceptions import ValidationError
import numpy as np
import pandas
from sqlalchemy import MetaData
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename

from metabulo import transform

def find(f, seq):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item): 
            return item
    return None
     

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
    id = fields.UUID(missing=uuid4)
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
    def table(self):
        if not hasattr(self, '_raw_table'):
            self._raw_table = pandas.read_csv(self.uri, header=None)
        return self._raw_table.copy()

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

    @property
    def index_row(self):
        return find(lambda r: r.row_type == TABLE_ROW_TYPES.INDEX, self.rows)

    @property
    def index_column(self):
        return find(lambda r: r.column_type == TABLE_COLUMN_TYPES.INDEX, self.columns)
    
    def filter_table_by_types(self, row_type, column_type):
        rows = CSVFile.get_indexes_by_type(self.rows, 'row', row_type)
        columns = CSVFile.get_indexes_by_type(self.columns, 'column', column_type)
        print(row_type, column_type)
        print(rows, columns)
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
        return self._save_csv_file_data(self.uri, table.to_csv(index=False, header=False))

    def _guess_table_structure(self):
        # TODO: a real implementation.  Pandas isn't adequate for this because of row metadata
        # Assume first row and first column are primary keys
        table_column_schema = TableColumnSchema()
        table = self.table
        row_half = floor(table.shape[0] / 2)
        col_half = floor(table.shape[1] / 2)

        columns = []
        index = 0
        keyfound = False
        for cell in table.iloc[row_half].fillna('').astype(str):
            if (len(cell) > 0 and not keyfound):
                keyfound = True
                column_type = TABLE_COLUMN_TYPES.INDEX
            elif (len(cell) == 0):
                column_type = TABLE_COLUMN_TYPES.MASK
            else:
                try:
                    floatcell = float(cell)
                    column_type = TABLE_COLUMN_TYPES.DATA
                except:
                    column_type = TABLE_COLUMN_TYPES.METADATA
            columns.append(
                table_column_schema.load({
                    'csv_file_id': self.id,
                    'column_index': index,
                    'column_type': column_type,
                })
            )
            index += 1

        table_row_schema = TableRowSchema()
        rows = []
        index = 0
        keyfound = False
        for cell in table.iloc[:,col_half].fillna('').astype(str):
            if (len(cell) > 0 and not keyfound):
                keyfound = True
                row_type = TABLE_ROW_TYPES.INDEX
            elif (len(cell) == 0):
                row_type = TABLE_ROW_TYPES.MASK
            else:
                try:
                    floatcell = float(cell)
                    row_type = TABLE_ROW_TYPES.DATA
                except:
                    row_type = TABLE_ROW_TYPES.METADATA
            rows.append(
                table_row_schema.load({
                    'csv_file_id': self.id,
                    'row_index': index,
                    'row_type': row_type,
                })
            )
            index += 1
        return rows, columns

    def modify_row_key(self, new_key_row_id):
        old_key_row = self.index_row
        new_key_row = find(lambda r: r.id == new_key_row_id, self.rows)
        if old_key_row is not None:
            old_key_row.row_type = TABLE_ROW_TYPES.METADATA
        new_key_row.row_type = TABLE_ROW_TYPES.INDEX

    def modify_column_key(self, new_key_column_id):
        old_key_column = self.index_column
        new_key_column = find(lambda r: r.id == new_key_column_id, self.columns)
        if old_key_column is not None:
            old_key_column.column_type = TABLE_COLUMN_TYPES.METADATA
        new_key_column.column_type = TABLE_COLUMN_TYPES.INDEX

    @classmethod
    def create_csv_file(cls, id, name, table, meta=None):
        csv_file = cls(id=id, name=name, meta=meta)
        cls._save_csv_file_data(csv_file.uri, table)
        rows, columns = csv_file._guess_table_structure()
        return csv_file, rows, columns
    
    @classmethod
    def get_indexes_by_type(cls, axis: Iterable, axis_name: str, axis_type: TableTypes):
        type_key = f'{axis_name}_type'
        index_key = f'{axis_name}_index'
        return [
            getattr(item, index_key) for item in axis
            if getattr(item, type_key) in (axis_type,)
        ]

    @classmethod
    def _save_csv_file_data(cls, uri, table_data):
        uri.parent.mkdir(parents=True, exist_ok=True)
        with open(uri, 'w') as f:
            f.write(table_data)
        return table_data


def _validate_table_data(table):
    try:
        pandas.read_csv(BytesIO(table.encode()))
    except Exception as e:
        raise ValidationError(str(e).strip(), data=table, field_name='table') from None


def _validate_name(name):
    if PurePath(name).suffix != '.csv':
        raise ValidationError('Only CSV files are allowed', data=name, field_name='name')


class CSVFileSchema(BaseSchema):
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

    index_row = fields.Nested('TableRowSchema', exclude=['csv_file'])
    index_column = fields.Nested('TableColumnSchema', exclude=['csv_file'])

    @post_load
    def fix_file_name(self, data):
        data['name'] = secure_filename(data['name'])
        return data

    @post_dump
    def read_csv_file(self, data):
        data['table'] = data['table'].to_csv(index=False, header=False)
        data['measurement_table'] = data['measurement_table'].to_csv(index=False, header=False)
        data['measurement_metadata'] = data['measurement_metadata'].to_csv(index=False, header=False)
        data['sample_metadata'] = data['sample_metadata'].to_csv(index=False, header=False)
        return data

    @post_load
    def make_object(self, data):
        csv_file, rows, columns = CSVFile.create_csv_file(**data)
        db.session.add(csv_file)
        db.session.add_all(rows + columns)
        return csv_file


class TableColumn(db.Model):
    __table_args__ = (
        UniqueConstraint('id', 'csv_file_id'),
    )
    id = db.Column(UUIDType(binary=False), default=uuid4)
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    column_index = db.Column(db.Integer, primary_key=True)
    column_type = db.Column(db.String, nullable=False)

    @property
    def column_header(self):
        if self.csv_file.index_row is not None:
            index = self.csv_file.index_row.row_index
            return self.csv_file.table.iat[index, self.column_index]
        return ''

    csv_file = db.relationship(
        CSVFile, backref=db.backref('columns', lazy=True, order_by='TableColumn.column_index'))


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn
    csv_file_id = fields.UUID(required=True, load_only=True)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    column_header = fields.Str(required=True, dump_only=True)
    
    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'transforms', 'index_row', 'index_column'], dump_only=True)



class ModifyColumnSchema(Schema):
    column_type = fields.Str(required=False, validate=validate.OneOf(TABLE_COLUMN_TYPES))

    @pre_load
    def validate_not_empty(self, data):
        if data is None or data == {}:
            raise ValidationError('JSON params required', data=data)
        return data


class TableRow(db.Model):
    __table_args__ = (
        UniqueConstraint('id', 'csv_file_id'),
    )

    id = db.Column(UUIDType(binary=False), default=uuid4)
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    row_type = db.Column(db.String, nullable=False)

    csv_file = db.relationship(
        CSVFile, backref=db.backref('rows', lazy=True, order_by='TableRow.row_index'))

    @property
    def row_name(self):
        if self.csv_file.index_column is not None:
            index = self.csv_file.index_column.column_index
            return self.csv_file.table.iat[self.row_index, index]
        return ''


class TableRowSchema(BaseSchema):
    __model__ = TableRow
    csv_file_id = fields.UUID(required=True, load_only=True)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    row_name = fields.Str(required=True, dump_only=True)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'transforms', 'index_row', 'index_column'], dump_only=True)


class ModifyRowSchema(Schema):
    row_type = fields.Str(required=False, validate=validate.OneOf(TABLE_ROW_TYPES))

    @pre_load
    def validate_not_empty(self, data):
        if data is None or data == {}:
            raise ValidationError('JSON params required', data=data)
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

    csv_file_id = fields.UUID(required=True, load_only=True)
    created = fields.DateTime(dump_only=True)
    transform_type = fields.Str(required=True, validate=validate.OneOf(transform.registry.keys()))
    args = fields.Dict(missing=dict)
    priority = fields.Float(required=True)

    csv_file = fields.Nested(CSVFileSchema, exclude=['transforms'], dump_only=True)

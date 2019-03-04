from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePath
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, Schema, validate
from marshmallow.exceptions import ValidationError
import numpy as np
import pandas
from sqlalchemy import MetaData
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

TABLE_COLUMN_TYPES = ['primary-id', 'secondary-id', 'numeric', 'qualitative']
TABLE_ROW_TYPES = ['header', 'sample', 'other']


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
    def raw_table(self):
        if not hasattr(self, '_raw_table'):
            self._raw_table = pandas.read_csv(self.uri, index_col=0)
        return self._raw_table.copy()

    @property
    def table(self):
        return self.apply_transforms(self.raw_table)

    @property
    def transforms(self):
        query = TableTransform.query.filter_by(csv_file_id=self.id)
        return query.order_by(TableTransform.priority)

    @property
    def uri(self):
        id = str(self.id)
        return Path(current_app.config['UPLOAD_FOLDER']) / id[:3] / id

    def apply_transforms(self, last=None):
        table = self.raw_table
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
        return self._save_csv_file_data(self.uri, table.to_csv())

    def _generate_table_columns(self):
        table_column_schema = TableColumnSchema()
        table = self.raw_table

        index = 0
        columns = []
        if table.index.name is not None:
            columns.append(
                table_column_schema.load({
                    'csv_file_id': self.id,
                    'column_header': table.index.name,
                    'column_index': 0,
                    'column_type': 'primary-id',
                    'column_mask': None
                })
            )
            index += 1
        for column_header, dtype in table.dtypes.items():
            if dtype == np.object:
                column_type = 'qualitative'
            else:
                column_type = 'numeric'

            columns.append(
                table_column_schema.load({
                    'csv_file_id': self.id,
                    'column_header': column_header,
                    'column_index': index,
                    'column_type': column_type,
                    'column_mask': False
                })
            )
            index += 1
        return columns

    def _generate_table_rows(self):
        table_row_schema = TableRowSchema()
        table = self.raw_table

        # Assuming the first row contains the header for the table.  Removing this assumption
        # would probably mean reading the table by something other than pandas.read_csv.
        rows = [
            table_row_schema.load({
                'csv_file_id': self.id,
                'row_id': '',  # or null?
                'row_index': 0,
                'row_type': 'header',
                'row_mask': None
            })
        ]

        # Assume all other rows are samples.  There may be other heuristics
        # to apply here in the future.  Or maybe mask rows with too many
        # NaN's.
        for index, row_id in enumerate(table.index):
            rows.append(
                table_row_schema.load({
                    'csv_file_id': self.id,
                    'row_id': row_id,
                    'row_index': index + 1,
                    'row_type': 'sample',
                    'row_mask': False
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

    @post_load
    def fix_file_name(self, data):
        data['name'] = secure_filename(data['name'])
        return data

    @post_dump
    def read_csv_file(self, data):
        data['table'] = data['table'].to_csv()
        return data

    @post_load
    def make_object(self, data):
        csv_file, rows, columns = CSVFile.create_csv_file(**data)
        db.session.add(csv_file)
        db.session.add_all(rows + columns)
        return csv_file


class TableColumn(db.Model):
    __table_args__ = (
        UniqueConstraint('column_header', 'csv_file_id'),
        UniqueConstraint('column_index', 'csv_file_id')
    )

    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    csv_file_id = db.Column(UUIDType(binary=False), db.ForeignKey('csv_file.id'), nullable=False)
    column_header = db.Column(db.String, nullable=False)
    column_index = db.Column(db.Integer, nullable=False)
    column_type = db.Column(db.String, nullable=False)
    column_mask = db.Column(db.Boolean, nullable=True)

    csv_file = db.relationship(CSVFile, backref=db.backref('columns', lazy=True))


class TableColumnSchema(BaseSchema):
    __model__ = TableColumn

    csv_file_id = fields.UUID(required=True, load_only=True)
    column_header = fields.Str(required=True, nullable=False)
    column_index = fields.Int(required=True, validate=validate.Range(min=0))
    column_type = fields.Str(required=True, validate=validate.OneOf(TABLE_COLUMN_TYPES))
    column_mask = fields.Bool(required=True, allow_none=True)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'transforms'], dump_only=True)


class TableRow(db.Model):
    __table_args__ = (
        UniqueConstraint('row_id', 'csv_file_id'),
        UniqueConstraint('row_index', 'csv_file_id')
    )

    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    csv_file_id = db.Column(
        UUIDType(binary=False), db.ForeignKey('csv_file.id'), nullable=False)
    row_id = db.Column(db.String, nullable=False)
    row_index = db.Column(db.Integer, nullable=False)
    row_type = db.Column(db.String, nullable=False)
    row_mask = db.Column(db.Boolean, nullable=True)

    csv_file = db.relationship(CSVFile, backref=db.backref('rows', lazy=True))


class TableRowSchema(BaseSchema):
    __model__ = TableRow

    csv_file_id = fields.UUID(required=True, load_only=True)
    row_id = fields.Str(required=True, nullable=False)
    row_index = fields.Int(required=True, validate=validate.Range(min=0))
    row_type = fields.Str(required=True, validate=validate.OneOf(TABLE_ROW_TYPES))
    row_mask = fields.Bool(required=True, allow_none=True)

    csv_file = fields.Nested(
        CSVFileSchema, exclude=['rows', 'columns', 'transforms'], dump_only=True)


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

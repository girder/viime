from datetime import datetime
import os
from uuid import uuid4

from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, post_dump, post_load, pre_load, Schema
from marshmallow.exceptions import ValidationError
import pandas
from sqlalchemy import MetaData
from sqlalchemy_utils.types.uuid import UUIDType
from werkzeug.utils import secure_filename


# This is to avoid having to manually name all constraints
# See: http://alembic.zzzcomputing.com/en/latest/naming.html
metadata = MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
})
db = SQLAlchemy(metadata=metadata)


class BaseSchema(Schema):
    __model__ = None

    id = fields.UUID()
    created = fields.DateTime(dump_only=True)

    @post_load
    def make_object(self, data):
        return self.__model__(**data)


class CSVFile(db.Model):
    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    name = db.Column(db.String, nullable=False)
    uri = db.Column(db.String, nullable=False)
    meta = db.Column(db.String, nullable=True)

    @property
    def table(self):
        return pandas.read_csv(self.uri)

    def save_table(self):
        table = self.table.to_csv()
        with open(self.uri, 'w') as f:
            f.write(table)
        return table


def _validate_uri(uri):
    try:
        pandas.read_csv(uri)
    except Exception as e:
        raise ValidationError(str(e).strip(), data=uri, field_name='uri') from None


class CSVFileSchema(BaseSchema):
    __model__ = CSVFile

    name = fields.Str(required=True)
    uri = fields.Str(required=True, validate=_validate_uri)
    table = fields.Raw(dump_only=True)
    meta = fields.Dict()

    @pre_load
    def remove_table_argument(self, data):
        if 'table' in data:
            del data['table']
        return data

    @post_dump
    def read_csv_file(self, data):
        data['table'] = data['table'].to_csv()
        return data


def _validate_name(name):
    if os.path.splitext(name)[-1] != '.csv':
        raise ValidationError('Only CSV files are allowed', data=name, field_name='name')


class CreateCSVFileSchema(Schema):
    name = fields.Str(required=True, validate=_validate_name)
    table = fields.Raw(missing='')
    meta = fields.Dict()

    @pre_load
    def fix_file_name(self, data):
        data['name'] = secure_filename(data['name'])
        return data

    @post_load
    def generate_uri(self, data):
        id = str(uuid4())
        uri = os.path.join(current_app.config['UPLOAD_FOLDER'], id)
        data['id'] = id
        data['uri'] = uri
        return data

from datetime import datetime
from io import BytesIO
from pathlib import Path, PurePath
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
    meta = db.Column(db.String, nullable=True)

    @property
    def table(self):
        return pandas.read_csv(self.uri, index_col=0)

    @property
    def uri(self):
        id = str(self.id)
        return Path(current_app.config['UPLOAD_FOLDER']) / id[:3] / id

    def save_table(self):
        return self._save_csv_file_data(self.uri, self.table.to_csv())

    @classmethod
    def create_csv_file(cls, id, name, table, meta=None):
        csv_file = cls(id=id, name=name, meta=meta)
        cls._save_csv_file_data(csv_file.uri, table)
        return csv_file

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
    __model__ = CSVFile.create_csv_file

    id = fields.Str(missing=uuid4)
    name = fields.Str(required=True, validate=_validate_name)
    table = fields.Raw(required=True, validate=_validate_table_data)
    meta = fields.Str()

    @pre_load
    def fix_file_name(self, data):
        data['name'] = secure_filename(data['name'])
        return data

    @post_dump
    def read_csv_file(self, data):
        data['table'] = data['table'].to_csv()
        return data

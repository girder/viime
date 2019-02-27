from flask import current_app
from marshmallow import fields, Schema, validates_schema
from marshmallow.exceptions import ValidationError
import pandas
from sklearn import preprocessing


class TransformExecutionError(Exception):
    pass


def dispatch(**kwargs):
    transform_type = kwargs.pop('transform_type', None)
    if transform_type is None:
        raise ValidationError(
            'transform_type must be provided', field_name='transform_type'
        )

    if transform_type not in registry:
        raise ValidationError(
            'Invalid transform type', data=transform_type, field_name='transform_type'
        )

    transform, schema = registry[transform_type]
    transform_args = schema.load(kwargs)
    try:
        return transform(**transform_args)
    except Exception as e:
        current_app.logger.exception(e)
        raise TransformExecutionError(str(e))


class BaseSchema(Schema):
    table = fields.Raw(validate=lambda table: isinstance(table, pandas.DataFrame))


class RowMixin:
    row = fields.String(required=True)

    @validates_schema
    def _validate_row(self, data):
        table = data['table']
        row = data['row']
        if row not in table.index:
            raise ValidationError(f'Invalid row name', data=row, field_name='row')


class ColumnMixin:
    column = fields.String(required=True)

    @validates_schema
    def _validate_column(self, data):
        table = data['table']
        column = data['column']
        if column not in table:
            raise ValidationError(f'Invalid column name', data=column, field_name='column')


def set_value(table, row, column, value):
    table.at[row, column] = value
    return table


class SetValueSchema(BaseSchema, RowMixin, ColumnMixin):
    value = fields.Float(required=True)


def normalize(table):
    for column in table:
        if str(table[column].dtype) != 'object':
            column_data = table[[column]].values.astype(float)
            min_max_scalar = preprocessing.MinMaxScaler()
            table[[column]] = min_max_scalar.fit_transform(column_data)
    return table


class NormalizeSchema(BaseSchema):
    pass


def fill_missing_values_by_constant(table, value):
    return table.fillna(value)


class FillMissingValuesByConstantSchema(BaseSchema):
    value = fields.Float(required=True)


def fill_missing_values_by_mean(table):
    for column in table:
        value = table[column].mean()
        table[column] = table[column].fillna(value)
    return table


registry = {
    'set_value': (set_value, SetValueSchema()),
    'normalize': (normalize, NormalizeSchema()),
    'fill_missing_values_by_constant': (
        fill_missing_values_by_constant, FillMissingValuesByConstantSchema()),
    'fill_missing_values_by_mean': (fill_missing_values_by_mean, BaseSchema()),
}

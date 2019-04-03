"""
This module contains methods related to validation of csv data contained
in the CSVFile model.
"""
from collections import namedtuple

from flask import current_app
from marshmallow import fields, post_dump, Schema, validate
from marshmallow.exceptions import ValidationError

from metabulo.cache import region

SEVERITY_VALUES = ['error', 'warning']
CONTEXT_VALUES = ['table', 'column', 'row']
TYPE_VALUES = [
    'primary-key-missing', 'header-missing', 'group-missing',
    'invalid-primary-key', 'invalid-header', 'non-numeric-data', 'invalid-group',
    'missing-data', 'low-variance'
]

_ValidationTuple = namedtuple(
    '_ValidationTuple', 'type_ title, severity context row_index column_index data')


class ValidationTuple(_ValidationTuple):
    def __new__(cls, **kwargs):
        kw = cls.defaults.copy()
        kw.update(kwargs)
        if kw.get('context') in ('table', 'column'):
            kw.setdefault('row_index', None)
        if kw.get('context') in ('table', 'row'):
            kw.setdefault('column_index', None)
        return _ValidationTuple.__new__(cls, **kw)


class PrimaryKeyMissing(ValidationTuple):
    defaults = {
        'title': 'No identifer column',
        'type_': 'primary-key-missing',
        'severity': 'error',
        'context': 'table',
        'data': None
    }


class HeaderMissing(ValidationTuple):
    defaults = {
        'title': 'No header row',
        'type_': 'header-missing',
        'severity': 'error',
        'context': 'table',
        'data': None
    }


class GroupMissing(ValidationTuple):
    defaults = {
        'title': 'No group column',
        'type_': 'group-missing',
        'severity': 'error',
        'context': 'table',
        'data': None
    }


class InvalidPrimaryKey(ValidationTuple):
    defaults = {
        'title': 'Invalid identifier',
        'type_': 'invalid-primary-key',
        'severity': 'error',
        'context': 'column'
    }


class InvalidHeader(ValidationTuple):
    defaults = {
        'title': 'Invalid header',
        'type_': 'invalid-header',
        'severity': 'error',
        'context': 'row'
    }


class InvalidGroup(ValidationTuple):
    defaults = {
        'title': 'Invalid group',
        'type_': 'invalid-group',
        'severity': 'error',
        'context': 'column'
    }


class NonNumericData(ValidationTuple):
    defaults = {
        'title': 'Non-numeric metabolite data',
        'type_': 'non-numeric-data',
        'severity': 'warning',
        'context': 'table'
    }


class MissingData(ValidationTuple):
    defaults = {
        'title': 'Missing data exceeds threshold',
        'type_': 'missing-data',
        'severity': 'warning'
    }


class LowVariance(ValidationTuple):
    defaults = {
        'title': 'Low data variance',
        'type_': 'low-variance',
        'severity': 'warning'
    }


class ValidationSchema(Schema):
    type_ = fields.Str(required=True, data_key='type')
    title = fields.Str(required=True)
    severity = fields.Str(required=True, validate=validate.OneOf(SEVERITY_VALUES))
    context = fields.Str(required=True, validate=validate.OneOf(CONTEXT_VALUES))
    row_index = fields.Int(required=False)
    column_index = fields.Int(required=False)
    group = fields.Str(required=False)
    data = fields.Raw(required=False)

    @post_dump
    def remove_null_values(self, data):
        return {k: v for k, v in data.items() if v is not None}


@region.cache_on_arguments()
def get_validation_list(csv_file):
    errors = []
    errors = _get_fatal_errors(csv_file)

    # We cannot proceed with warnings when the table is not parsed correctly.
    if not errors:
        errors = _get_warnings(csv_file)

    validation_schema = ValidationSchema()
    try:
        return validation_schema.dump(errors, many=True)
    except ValidationError as e:
        # This is an internal error so log the validation error and return
        # a 500 to the endpoint.
        current_app.logger.exception(e)
        raise Exception('Could not serialize validation object')


def _get_fatal_errors(csv_file):
    errors = []
    if csv_file.header_row_index is None:
        errors.append(PrimaryKeyMissing())
    if csv_file.key_column_index is None:
        errors.append(HeaderMissing())
    if csv_file.group_column_index is None:
        errors.append(GroupMissing())
    return errors


def _get_warnings(csv_file):
    return []

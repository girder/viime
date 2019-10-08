"""
This module contains methods related to validation of csv data contained
in the CSVFile model.
"""
from collections import namedtuple

from marshmallow import fields, post_dump, Schema, validate
from pandas import Index, to_numeric

from viime.cache import region

SEVERITY_VALUES = ['error', 'warning']
CONTEXT_VALUES = ['table', 'column', 'row']
TYPE_VALUES = [
    'primary-key-missing', 'header-missing', 'group-missing',
    'invalid-primary-key', 'invalid-header', 'non-numeric-data', 'invalid-group',
    'missing-data', 'low-variance'
]

_ValidationTuple = namedtuple(
    '_ValidationTuple', 'type_ title, severity context row_index column_index data')

GROUP_MISSING_THRESHOLD = 0.25
LOW_VARIANCE_THRESHOLD = 1e-8
MAX_NAN_THRESHOLD = 0.95


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


class NonNumericRow(ValidationTuple):
    defaults = {
        'title': 'Non-numeric row',
        'type_': 'non-numeric-row',
        'severity': 'error',
        'context': 'row'
    }


class NonNumericColumn(ValidationTuple):
    defaults = {
        'title': 'Non-numeric column',
        'type_': 'non-numeric-column',
        'severity': 'error',
        'context': 'column'
    }


class NonNumericData(ValidationTuple):
    defaults = {
        'title': 'Non-numeric data',
        'type_': 'non-numeric-data',
        'severity': 'warning',
        'context': 'table'
    }


class MissingData(ValidationTuple):
    defaults = {
        'title': 'Missing data',
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
    def remove_null_values(self, data, **kwargs):
        return {k: v for k, v in data.items() if v is not None}


def get_validation_list(csv_file):
    errors = get_fatal_index_errors(csv_file)

    if not errors:
        errors = get_warnings(csv_file)

    return errors


def get_missing_index_errors(csv_file):
    errors = []
    if csv_file.key_column_index is None:
        errors.append(PrimaryKeyMissing())
    if csv_file.header_row_index is None:
        errors.append(HeaderMissing())
    if csv_file.group_column_index is None:
        errors.append(GroupMissing())
    return errors


@region.cache_on_arguments()
def get_fatal_index_errors(csv_file):
    errors = get_missing_index_errors(csv_file)
    if not errors:
        errors = get_invalid_index_errors(csv_file)
    if not errors:
        errors = get_non_numeric_errors(csv_file)
    return errors


def check_valid_index(series):
    """Check if pandas series can be a valid index."""
    index = Index(series)
    if index.hasnans:
        return "Contains NaN's"
    if not index.is_unique:
        return 'Values are not unique'


def check_valid_groups(groups):
    index = Index(groups.iloc[:, 0])
    if index.hasnans or index.contains(''):
        return 'Contains empty values'


def get_invalid_index_errors(csv_file):
    from viime.models import TABLE_COLUMN_TYPES, TABLE_ROW_TYPES

    errors = []
    table = csv_file.filter_table_by_types(
        TABLE_ROW_TYPES.DATA, TABLE_COLUMN_TYPES.INDEX).iloc[:, 0]
    error_data = check_valid_index(table)
    if error_data:
        errors.append(InvalidPrimaryKey(column_index=csv_file.key_column_index, data=error_data))

    table = csv_file.filter_table_by_types(
        TABLE_ROW_TYPES.INDEX, TABLE_COLUMN_TYPES.DATA).iloc[0, :]
    error_data = check_valid_index(table)
    if error_data:
        errors.append(InvalidHeader(row_index=csv_file.header_row_index, data=error_data))

    error_data = check_valid_groups(csv_file.groups)
    if error_data:
        errors.append(InvalidGroup(column_index=csv_file.group_column_index, data=error_data))

    return errors


def get_non_numeric_errors(csv_file):
    errors = []
    raw_table = csv_file.raw_measurement_table

    for index in range(raw_table.shape[0]):
        row = to_numeric(raw_table.iloc[index, :], errors='coerce')
        nans = (row != row).sum()
        if nans / raw_table.shape[1] > MAX_NAN_THRESHOLD:
            row = csv_file.get_row_by_name(raw_table.index[index])
            errors.append(
                NonNumericRow(row_index=row.row_index,
                              data=f'Contains {nans} non-numeric values')
            )

    for index in range(raw_table.shape[1]):
        column = to_numeric(raw_table.iloc[:, index], errors='coerce')
        nans = (column != column).sum()
        if nans / raw_table.shape[0] > MAX_NAN_THRESHOLD:
            column = csv_file.get_column_by_name(raw_table.columns[index])
            errors.append(
                NonNumericColumn(column_index=column.column_index,
                                 data=f'Contains {nans} non-numeric values')
            )
    return errors


def _count_non_numeric(value):
    try:
        float(value)
        return 0
    except ValueError:
        return 1


@region.cache_on_arguments()
def get_warnings(csv_file):
    warnings = get_non_numeric_warnings(csv_file)
    warnings.extend(get_missing_percent_warnings(csv_file))
    warnings.extend(get_low_variance_warnings(csv_file))
    return warnings


def get_non_numeric_warnings(csv_file):
    warnings = []
    non_numeric_count = int(csv_file.raw_measurement_table.applymap(_count_non_numeric).sum().sum())
    if non_numeric_count > 0:
        # maybe return actual indices if useful to the client
        warnings.append(
            NonNumericData(data=f'{non_numeric_count} elements contain non-numeric data')
        )
    return warnings


def get_missing_percent_warnings(csv_file):
    table = csv_file.raw_measurement_table
    groups = csv_file.groups

    q = (table != table).join(groups).groupby(groups.columns[0])
    total = q.count()
    missing = q.agg('sum')
    percent_missing = missing / total
    over_threshold = (percent_missing > GROUP_MISSING_THRESHOLD).all()

    warnings = []
    for column_name, warn in over_threshold.items():
        if not warn:
            continue
        column = csv_file.get_column_by_name(column_name)
        warnings.append(
            MissingData(
                context='column',
                column_index=column.column_index,
                data=f'All groups exceed {int(GROUP_MISSING_THRESHOLD * 100)}% missing data'
            )
        )
    return warnings


def get_low_variance_warnings(csv_file):
    table = csv_file.raw_measurement_table
    warnings = []

    for column_name, value in table.var().items():
        if value != value or value > LOW_VARIANCE_THRESHOLD:
            continue

        column = csv_file.get_column_by_name(column_name)
        warnings.append(
            LowVariance(
                context='column',
                column_index=column.column_index,
                data=f'Low column data variance ({value:.2e})'
            )
        )
    return warnings

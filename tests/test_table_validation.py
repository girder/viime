from pytest import fixture

from metabulo.models import db, TABLE_COLUMN_TYPES, TABLE_ROW_TYPES
from metabulo.table_validation import get_validation_list, ValidationSchema

validation_schema = ValidationSchema()


@fixture
def valid_table(pathological_table):
    pathological_table.rows[0].row_type = TABLE_ROW_TYPES.MASK
    pathological_table.rows[1].row_type = TABLE_ROW_TYPES.MASK
    pathological_table.rows[2].row_type = TABLE_ROW_TYPES.INDEX
    pathological_table.rows[3].row_type = TABLE_ROW_TYPES.METADATA
    pathological_table.rows[10].row_type = TABLE_ROW_TYPES.MASK

    pathological_table.columns[0].column_type = TABLE_COLUMN_TYPES.MASK
    pathological_table.columns[1].column_type = TABLE_COLUMN_TYPES.INDEX
    pathological_table.columns[2].column_type = TABLE_COLUMN_TYPES.GROUP

    db.session.add_all(pathological_table.rows)
    db.session.add_all(pathological_table.columns)
    db.session.add(pathological_table)
    db.session.commit()
    yield pathological_table


def test_no_index(csv_file):
    index_column = csv_file.columns[0]
    index_column.column_type = TABLE_COLUMN_TYPES.MASK
    db.session.add(index_column)
    db.session.commit()

    validation_list = validation_schema.dump(get_validation_list(csv_file), many=True)
    assert validation_list == [{
        'context': 'table',
        'severity': 'error',
        'title': 'No identifer column',
        'type': 'primary-key-missing'
    }]


def test_no_header(csv_file):
    header_row = csv_file.rows[0]
    header_row.row_type = TABLE_ROW_TYPES.MASK
    db.session.add(header_row)
    db.session.commit()

    validation_list = validation_schema.dump(get_validation_list(csv_file), many=True)
    assert validation_list == [{
        'context': 'table',
        'severity': 'error',
        'title': 'No header row',
        'type': 'header-missing'
    }]


def test_no_group(csv_file):
    group_column = csv_file.columns[1]
    group_column.column_type = TABLE_COLUMN_TYPES.MASK
    db.session.add(group_column)
    db.session.commit()

    validation_list = validation_schema.dump(get_validation_list(csv_file), many=True)
    assert validation_list == [{
        'context': 'table',
        'severity': 'error',
        'title': 'No group column',
        'type': 'group-missing'
    }]


def test_invalid_index(valid_table):
    column = valid_table.columns[0]
    column.column_type = TABLE_COLUMN_TYPES.INDEX
    db.session.add(column)
    db.session.commit()

    validation_list = validation_schema.dump(get_validation_list(valid_table), many=True)
    assert validation_list == [{
        'context': 'column',
        'severity': 'error',
        'title': 'Invalid identifier',
        'type': 'invalid-primary-key',
        'column_index': 0,
        'data': 'Contains NaN\'s'
    }]


def test_invalid_group(valid_table):
    column = valid_table.columns[0]
    column.column_type = TABLE_COLUMN_TYPES.GROUP
    db.session.add(column)
    db.session.commit()

    validation_list = validation_schema.dump(get_validation_list(valid_table), many=True)
    assert validation_list == [{
        'context': 'column',
        'severity': 'error',
        'title': 'Invalid group',
        'type': 'invalid-group',
        'column_index': 0,
        'data': 'Contains empty values'
    }]


def test_multiple_missing_errors(pathological_table):
    pathological_table.rows[0].row_type = TABLE_ROW_TYPES.MASK

    pathological_table.columns[0].column_type = TABLE_COLUMN_TYPES.MASK
    pathological_table.columns[1].column_type = TABLE_COLUMN_TYPES.MASK

    db.session.add_all(pathological_table.rows)
    db.session.add_all(pathological_table.columns)
    db.session.add(pathological_table)
    db.session.commit()

    validation_list = validation_schema.dump(get_validation_list(pathological_table), many=True)

    assert validation_list == [
        {
            'severity': 'error',
            'type': 'primary-key-missing',
            'title': 'No identifer column',
            'context': 'table'
        },
        {
            'severity': 'error',
            'type': 'header-missing',
            'title': 'No header row',
            'context': 'table'
        },
        {
            'severity': 'error',
            'type': 'group-missing',
            'title': 'No group column',
            'context': 'table'
        }
    ]


def test_multiple_invalid_errors(pathological_table):
    validation_list = validation_schema.dump(get_validation_list(pathological_table), many=True)
    assert validation_list == [
        {
            'context': 'column',
            'column_index': 0,
            'type': 'invalid-primary-key',
            'data': 'Contains NaN\'s',
            'title': 'Invalid identifier',
            'severity': 'error'
        },
        {
            'context': 'column',
            'column_index': 1,
            'type': 'invalid-group',
            'data': 'Contains empty values',
            'title': 'Invalid group',
            'severity': 'error'
        }
    ]

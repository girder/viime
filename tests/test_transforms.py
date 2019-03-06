from io import BytesIO
from math import nan

import pandas
from pandas.testing import assert_frame_equal
import pytest

from metabulo import transform
from metabulo.models import db


@pytest.fixture
def table(app):
    with app.app_context():
        yield pandas.read_csv(BytesIO(b"""
id,col1,col2
row1,0.5,2.0
row2,1.5,0.0
"""), index_col=0)


def test_set_value(table):
    t = transform.set_value(table, 'row1', 'col2', 100)
    assert t.at['row1', 'col2'] == 100


def test_normalize(table):
    correct = table.copy()
    correct[:] = [[0.0, 1.0], [1.0, 0.0]]
    t = transform.normalize(table)
    assert_frame_equal(t, correct)


def test_fill_missing_value_by_mean(table):
    table.at['row1', 'col2'] = nan
    t = transform.fill_missing_values_by_mean(table)
    assert t.at['row1', 'col2'] == 0


def test_fill_missing_value_by_constant(table):
    table.at['row1', 'col2'] = nan
    t = transform.fill_missing_values_by_constant(table, -100)
    assert t.at['row1', 'col2'] == -100


def test_dispatch(table):
    t = transform.dispatch(
        table=table,
        transform_type='set_value',
        row='row1',
        column='col1',
        value=10
    )
    assert t.at['row1', 'col1'] == 10


def test_dispatch_no_transform_type_error(table):
    with pytest.raises(transform.ValidationError):
        transform.dispatch(
            table=table
        )


def test_dispatch_invalid_argument_error(table):
    with pytest.raises(transform.ValidationError):
        transform.dispatch(
            table=table,
            transform_type='invalid'
        )


def test_generate_transform(csv_file):
    table = csv_file.table
    table.at['row1', 'col2'] = nan
    csv_file.save_table(table)

    t1 = csv_file.generate_transform({
        'transform_type': 'fill_missing_values_by_constant',
        'value': -3,
        'priority': 1
    })
    db.session.add(t1)

    t2 = csv_file.generate_transform({
        'transform_type': 'normalize',
        'priority': 2
    })
    db.session.add(t2)

    correct = table.copy()
    correct[:] = [[0.0, 0.0], [1.0, 1.0]]
    assert_frame_equal(csv_file.measurement_table, correct)

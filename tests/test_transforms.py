from io import BytesIO

from flask import url_for
import pandas
from pandas.testing import assert_frame_equal
import pytest

from metabulo import normalization


@pytest.fixture
def table(app):
    with app.app_context():
        yield pandas.read_csv(BytesIO(b"""
id,col1,col2
row1,0.5,2.0
row2,1.5,0.0
"""), index_col=0)


def test_normalize_minmax(table):
    correct = table.copy()
    correct[:] = [[0.0, 1.0], [1.0, 0.0]]
    t = normalization.normalize('minmax', table)
    assert_frame_equal(t, correct)


def test_normalize_none(table):
    correct = table.copy()
    t = normalization.normalize(None, table)
    assert_frame_equal(t, correct)


def test_normalize_api(client, csv_file):
    resp = client.put(
        url_for('csv.set_normalization_method', csv_id=csv_file.id), json={'method': 'minmax'}
    )
    assert resp.status_code == 200
    assert resp.json['normalization'] == 'minmax'
    assert resp.json['measurement_table'] == 'id,col1,col2\nrow1,0.0,1.0\nrow2,1.0,0.0\n'

    resp = client.put(
        url_for('csv.set_normalization_method', csv_id=csv_file.id), json={'method': None}
    )
    assert resp.status_code == 200
    assert resp.json['normalization'] is None
    assert resp.json['measurement_table'] == 'id,col1,col2\nrow1,0.5,2.0\nrow2,1.5,0.0\n'

from flask import url_for
import pytest

from metabulo.models import CSVFileSchema, db

csv_file_schema = CSVFileSchema()

table_data = """
id,meta,col1,col2
row1,a,0.5,2.0
row2,b,1.5,0
row3,b,4,0.5
"""


@pytest.fixture
def table(client):
    csv_file = csv_file_schema.load({
        'table': table_data,
        'name': 'test_csv_file.csv'
    })
    db.session.add(csv_file)
    db.session.commit()
    yield csv_file


def test_list_columns(client, table):
    resp = client.get(
        url_for('csv.list_columns', csv_id=table.id))
    assert resp.status_code == 200
    assert resp.json == [{
        'column_header': 'id',
        'column_index': 0,
        'column_type': 'key'
    }, {
        'column_header': 'meta',
        'column_index': 1,
        'column_type': 'metadata'
    }, {
        'column_header': 'col1',
        'column_index': 2,
        'column_type': 'measurement'
    }, {
        'column_header': 'col2',
        'column_index': 3,
        'column_type': 'measurement'
    }]


def test_list_rows(client, table):
    resp = client.get(
        url_for('csv.list_rows', csv_id=table.id))
    assert resp.status_code == 200
    assert resp.json == [{
        'row_name': 'id',
        'row_index': 0,
        'row_type': 'header'
    }, {
        'row_name': 'row1',
        'row_index': 1,
        'row_type': 'sample'
    }, {
        'row_name': 'row2',
        'row_index': 2,
        'row_type': 'sample'
    }, {
        'row_name': 'row3',
        'row_index': 3,
        'row_type': 'sample'
    }]


def test_get_column(client, table):
    resp = client.get(
        url_for('csv.get_column', csv_id=table.id, column_index=1))
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'meta',
        'column_index': 1,
        'column_type': 'metadata'
    }


def test_get_row(client, table):
    resp = client.get(
        url_for('csv.get_row', csv_id=table.id, row_index=1))
    assert resp.status_code == 200
    assert resp.json == {
        'row_name': 'row1',
        'row_index': 1,
        'row_type': 'sample'
    }


def test_modify_column(client, table):
    resp = client.put(
        url_for('csv.modify_column', csv_id=table.id, column_index=1),
        json={
            'column_type': 'metadata'
        }
    )
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'meta',
        'column_index': 1,
        'column_type': 'metadata'
    }


def test_modify_row(client, table):
    resp = client.put(
        url_for('csv.modify_row', csv_id=table.id, row_index=1),
        json={
            'row_type': 'masked'
        }
    )
    assert resp.status_code == 200
    assert resp.json == {
        'row_name': 'row1',
        'row_index': 1,
        'row_type': 'masked'
    }

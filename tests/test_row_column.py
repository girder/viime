from flask import url_for
import pytest

from viime.models import CSVFileSchema, db

csv_file_schema = CSVFileSchema()

table_data = """
id,group,meta,col1,col2
row1,g1,a,0.5,2.0
row2,g1,b,1.5,0
row3,g2,b,4,-2.0
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
        'column_header': 'group',
        'column_index': 1,
        'column_type': 'group'
    }, {
        'column_header': 'meta',
        'column_index': 2,
        'column_type': 'measurement'
    }, {
        'column_header': 'col1',
        'column_index': 3,
        'column_type': 'measurement'
    }, {
        'column_header': 'col2',
        'column_index': 4,
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
        url_for('csv.get_column', csv_id=table.id, column_index=3))
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'col1',
        'column_index': 3,
        'column_type': 'measurement'
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
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={'changes': [{'context': 'column', 'index': 1, 'label': 'metadata'}]}
    )
    assert resp.status_code == 200

    # Right now columns[1] is column_index=1, but it would be nice
    # to know if that breaks.
    resp = client.get(
        url_for('csv.get_csv_file', csv_id=table.id)
    )
    assert resp.status_code == 200
    assert resp.json['columns'][1]['column_type'] == 'metadata'


def test_modify_row(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={'changes': [{'context': 'row', 'index': 1, 'label': 'masked'}]}
    )
    assert resp.status_code == 200

    resp = client.get(
        url_for('csv.get_csv_file', csv_id=table.id)
    )
    assert resp.status_code == 200
    assert resp.json['rows'][1]['row_type'] == 'masked'


def test_batch_modify_in_order(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={
            'changes': [
                {'context': 'row', 'index': 1, 'label': 'masked'},
                {'context': 'row', 'index': 1, 'label': 'sample'},
            ]
        }
    )
    assert resp.status_code == 200

    resp = client.get(
        url_for('csv.get_csv_file', csv_id=table.id)
    )
    assert resp.status_code == 200
    assert resp.json['rows'][1]['row_type'] == 'sample'


def test_batch_modify_invalid_state(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={
            'changes': [
                {'context': 'row', 'index': 0, 'label': 'masked'},
                {'context': 'row', 'index': 1, 'label': 'header'},
                {'context': 'row', 'index': 1, 'label': 'sample'},
            ]
        }
    )
    assert resp.status_code == 200

    resp = client.get(
        url_for('csv.get_csv_file_validation', csv_id=table.id)
    )
    assert resp.status_code == 200
    assert len(resp.json) > 0


def test_batch_modify_row_and_column(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={
            'changes': [
                {'context': 'row', 'index': 1, 'label': 'masked'},
                {'context': 'column', 'index': 2, 'label': 'masked'},
            ]
        }
    )
    assert resp.status_code == 200

    resp = client.get(
        url_for('csv.get_csv_file', csv_id=table.id)
    )
    assert resp.status_code == 200
    assert resp.json['rows'][1]['row_type'] == 'masked'
    assert resp.json['columns'][2]['column_type'] == 'masked'
    assert len(resp.json['table_validation']) == 0


def test_batch_modify_bogus_labels(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={
            'changes': [
                {'context': 'row', 'index': 1, 'label': 'bogus'},
                {'context': 'row', 'index': 2, 'label': 'masked'}
            ]
        }
    )
    assert resp.status_code == 400
    assert 'rows' not in resp.json

    # Verify that the second, well-formed change did not take effect
    resp = client.get(
        url_for('csv.get_row', csv_id=table.id, row_index=2))
    assert resp.status_code == 200
    assert resp.json['row_type'] != 'masked'

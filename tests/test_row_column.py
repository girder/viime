from flask import url_for
import pytest

from metabulo.models import CSVFile, CSVFileSchema, db

csv_file_schema = CSVFileSchema()

table_data = """
id,group,meta,col1,col2
row1,g1,a,0.5,2.0
row2,g1,b,1.5,0
row3,g2,b,4,0.5
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
        url_for('csv.get_column', csv_id=table.id, column_index=2))
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'meta',
        'column_index': 2,
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
        url_for('csv.modify_column', csv_id=table.id, column_index=1),
        json={
            'column_type': 'metadata'
        }
    )
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'group',
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


def test_delete_key_column(client, table):
    resp = client.put(
        url_for('csv.modify_column', csv_id=table.id, column_index=0),
        json={
            'column_type': 'metadata'
        }
    )
    assert resp.status_code == 200
    assert resp.json['column_type'] == 'metadata'


def test_delete_header_row(client, table):
    resp = client.put(
        url_for('csv.modify_row', csv_id=table.id, row_index=0),
        json={
            'row_type': 'metadata'
        }
    )
    assert resp.status_code == 200
    assert resp.json['row_type'] == 'metadata'


def test_modify_group_column(client, table):
    resp = client.put(
        url_for('csv.modify_column', csv_id=table.id, column_index=2),
        json={
            'column_type': 'group'
        }
    )
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'meta',
        'column_index': 2,
        'column_type': 'group'
    }

    resp = client.get(
        url_for('csv.get_column', csv_id=table.id, column_index=1)
    )
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'group',
        'column_index': 1,
        'column_type': 'metadata'
    }


def test_modify_csv_file_header_index(client):
    table = """
,,,
row1,g,0.5,2.0
row2,g,1.5,0
id,g,header1,header2
"""
    csv_file = csv_file_schema.load({
        'table': table,
        'name': 'test_csv_file.csv'
    })
    db.session.add(csv_file)
    db.session.commit()

    csv_id = csv_file.id
    resp = client.put(
        url_for('csv.modify_row', csv_id=csv_id, row_index=0),
        json={'row_type': 'masked'}
    )
    assert resp.status_code == 200

    resp = client.put(
        url_for('csv.modify_row', csv_id=csv_id, row_index=3),
        json={'row_type': 'header'}
    )
    assert resp.status_code == 200
    assert (CSVFile.query.get(csv_id).measurement_table.columns == ['header1', 'header2']).all()


def test_modify_csv_file_key_index(client):
    table = """
header1,group,id,header2,header3,extra
0,a,row1,0.5,2.0,
0,b,row2,1.5,0,
"""
    csv_file = csv_file_schema.load({
        'table': table,
        'name': 'test_csv_file.csv'
    })
    db.session.add(csv_file)
    db.session.commit()

    csv_id = csv_file.id
    resp = client.put(
        url_for('csv.modify_column', csv_id=csv_id, column_index=2),
        json={'column_type': 'key'}
    )
    assert resp.status_code == 200

    resp = client.put(
        url_for('csv.modify_column', csv_id=csv_id, column_index=5),
        json={'column_type': 'masked'}
    )
    assert resp.status_code == 200
    assert (CSVFile.query.get(csv_id).measurement_table.columns == ['header2', 'header3']).all()

    resp = client.put(
        url_for('csv.modify_column', csv_id=csv_id, column_index=0),
        json={'column_type': 'measurement'}
    )
    assert resp.status_code == 200
    assert (CSVFile.query.get(csv_id).measurement_table.columns ==
            ['header1', 'header2', 'header3']).all()

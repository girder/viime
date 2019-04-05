from flask import url_for
import pytest

from metabulo.models import CSVFileSchema, db

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
        'column_type': 'key',
        'data_column_index': None,
        'data_variance': None,
        'missing_percent': None
    }, {
        'column_header': 'group',
        'column_index': 1,
        'column_type': 'group',
        'data_column_index': None,
        'data_variance': None,
        'missing_percent': None
    }, {
        'column_header': 'meta',
        'column_index': 2,
        'column_type': 'measurement',
        'data_column_index': 0,
        'data_variance': None,
        'missing_percent': 1.0
    }, {
        'column_header': 'col1',
        'column_index': 3,
        'column_type': 'measurement',
        'data_column_index': 1,
        'data_variance': 3.25,
        'missing_percent': 0.0
    }, {
        'column_header': 'col2',
        'column_index': 4,
        'column_type': 'measurement',
        'data_column_index': 2,
        'data_variance': 4.0,
        'missing_percent': 0.0
    }]


def test_list_rows(client, table):
    resp = client.get(
        url_for('csv.list_rows', csv_id=table.id))
    assert resp.status_code == 200
    assert resp.json == [{
        'row_name': 'id',
        'row_index': 0,
        'row_type': 'header',
        'data_row_index': None
    }, {
        'row_name': 'row1',
        'row_index': 1,
        'row_type': 'sample',
        'data_row_index': 0
    }, {
        'row_name': 'row2',
        'row_index': 2,
        'row_type': 'sample',
        'data_row_index': 1
    }, {
        'row_name': 'row3',
        'row_index': 3,
        'row_type': 'sample',
        'data_row_index': 2
    }]


def test_get_column(client, table):
    resp = client.get(
        url_for('csv.get_column', csv_id=table.id, column_index=3))
    assert resp.status_code == 200
    assert resp.json == {
        'column_header': 'col1',
        'column_index': 3,
        'column_type': 'measurement',
        'data_column_index': 1,
        'data_variance': 3.25,
        'missing_percent': 0.0
    }


def test_get_row(client, table):
    resp = client.get(
        url_for('csv.get_row', csv_id=table.id, row_index=1))
    assert resp.status_code == 200
    assert resp.json == {
        'row_name': 'row1',
        'row_index': 1,
        'row_type': 'sample',
        'data_row_index': 0
    }


def test_modify_column(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={'changes': [{'context': 'column', 'index': 1, 'label': 'metadata'}]}
    )
    assert resp.status_code == 200
    # Right now columns[1] is column_index=1, but it would be nice
    # to know if that breaks.
    assert resp.json['columns'][1]['column_type'] == 'metadata'


def test_modify_row(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={'changes': [{'context': 'row', 'index': 1, 'label': 'masked'}]}
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
    assert resp.json['rows'][1]['row_type'] == 'sample'

def test_batch_modify_invalid_state(client, table):
    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={
            'changes': [
                {'context': 'row', 'index': 1, 'label': 'header'},
                {'context': 'row', 'index': 1, 'label': 'sample'},
            ]
        }
    )
    assert resp.status_code == 200

# def test_delete_key_column(client, table):
#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=table.id),
#         json={'changes': [{'context': 'column', 'index': 0, 'label': 'metadata'}]}
#     )
#     assert resp.status_code == 200
#     assert resp.json['column_type'] == 'metadata'


# def test_delete_header_row(client, table):
#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=table.id),
#         json={'changes': [{'context': 'row', 'index': 0, 'label': 'metadata'}]}
#     )
#     assert resp.status_code == 200
#     assert resp.json['row_type'] == 'metadata'


# def test_modify_group_column(client, table):
#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=table.id),
#         json={'changes': [{'context': 'column', 'index': 2, 'label': 'group'}]}
#     )
#     assert resp.status_code == 200
#     assert resp.json == {
#         'column_header': 'meta',
#         'column_index': 2,
#         'column_type': 'group',
#         'data_column_index': None,
#         'data_variance': None,
#         'missing_percent': None
#     }

#     resp = client.get(
#         url_for('csv.get_column', csv_id=table.id, column_index=1)
#     )
#     assert resp.status_code == 200
#     assert resp.json == {
#         'column_header': 'group',
#         'column_index': 1,
#         'column_type': 'metadata',
#         'data_column_index': None,
#         'data_variance': None,
#         'missing_percent': None
#     }


# def test_modify_csv_file_header_index(client):
#     table = """
# ,,,
# row1,g,0.5,2.0
# row2,g,1.5,0
# id,g,header1,header2
# """
#     csv_file = csv_file_schema.load({
#         'table': table,
#         'name': 'test_csv_file.csv'
#     })
#     db.session.add(csv_file)
#     db.session.commit()

#     csv_id = csv_file.id
#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=csv_id),
#         json={'changes': [{'context': 'row', 'index': 0, 'label': 'masked'}]}
#     )
#     assert resp.status_code == 200

#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=csv_id),
#         json={'changes': [{'context': 'row', 'index': 3, 'label': 'header'}]}
#     )
#     assert resp.status_code == 200
#     assert (CSVFile.query.get(csv_id).measurement_table.columns == ['header1', 'header2']).all()


# def test_modify_csv_file_key_index(client):
#     table = """
# header1,group,id,header2,header3,extra
# 0,a,row1,0.5,2.0,
# 0,b,row2,1.5,0,
# """
#     csv_file = csv_file_schema.load({
#         'table': table,
#         'name': 'test_csv_file.csv'
#     })
#     db.session.add(csv_file)
#     db.session.commit()

#     csv_id = csv_file.id
#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=csv_id),
#         json={'changes': [{'context': 'column', 'index': 2, 'label': 'key'}]}
#     )
#     assert resp.status_code == 200

#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=csv_id),
#         json={'changes': [{'context': 'column', 'index': 5, 'label': 'masked'}]}
#     )
#     assert resp.status_code == 200
#     assert (CSVFile.query.get(csv_id).measurement_table.columns == ['header2', 'header3']).all()

#     resp = client.put(
#         url_for('csv.batch_modify_label', csv_id=csv_id),
#         json={'changes': [{'context': 'column', 'index': 0, 'label': 'measurement'}]}
#     )
#     assert resp.status_code == 200
#     assert (CSVFile.query.get(csv_id).measurement_table.columns ==
#             ['header1', 'header2', 'header3']).all()

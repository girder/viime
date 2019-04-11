from io import BytesIO

from flask import url_for

from metabulo.models import CSVFile

csv_data = """
id,col1,col2
row1,0.5,2.0
row2,1.5,0
"""


def test_upload_csv_file(client):
    data = {
        'file': (BytesIO(csv_data.encode()), 'test_file1.csv'),
        'meta': '{"foo": "bar"}'
    }
    resp = client.post(
        url_for('csv.upload_csv_file'), data=data, content_type='multipart/form-data')

    assert resp.status_code == 201
    assert resp.json['name'] == 'test_file1.csv'
    assert csv_data.strip().startswith('id,col1,col2')
    assert len(resp.json['columns']) == 3
    assert resp.json['meta'] == {'foo': 'bar'}


def test_post_csv_data(client):
    data = {
        'name': 'test_file1.csv',
        'table': csv_data
    }
    resp = client.post(
        url_for('csv.create_csv_file'), json=data)

    assert resp.status_code == 201
    assert resp.json['name'] == 'test_file1.csv'
    assert csv_data.strip().startswith('id,col1,col2')
    assert len(resp.json['columns']) == 3


def test_download_csv_file(client, csv_file):
    resp = client.get(
        url_for('csv.download_csv_file', csv_id=csv_file.id)
    )

    assert resp.status_code == 200
    assert 'text/csv' in resp.headers['Content-Type']
    assert resp.headers['Content-Disposition'] == f'attachment; filename={csv_file.name}'


def test_get_csv_file(client, csv_file):
    resp = client.get(
        url_for('csv.get_csv_file', csv_id=csv_file.id)
    )

    assert resp.status_code == 200
    assert 'application/json' in resp.headers['Content-Type']
    assert resp.json['table'] == csv_file.table.to_csv(header=False, index=False)


def test_delete_csv_file(client, csv_file):
    resp = client.delete(
        url_for('csv.delete_csv_file', csv_id=csv_file.id)
    )

    assert resp.status_code == 204
    assert CSVFile.query.first() is None


def test_post_csv_file_error(client):
    data = {
        'file': (b'', 'test_file1.csv')
    }
    resp = client.post(
        url_for('csv.upload_csv_file'), data=data, content_type='multipart/form-data')

    assert resp.status_code == 400
    assert resp.json == {'table': ['No columns to parse from file']}


def test_row_order_after_reindexing(client, pathological_table):
    table = pathological_table
    resp = client.get(url_for('csv.get_csv_file', csv_id=table.id))
    assert resp.status_code == 200

    table_from_api = resp.json['table']

    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={'changes': [{'context': 'column', 'index': 1, 'label': 'key'}]}
    )
    assert resp.status_code == 200

    resp = client.get(url_for('csv.get_csv_file', csv_id=table.id))
    assert resp.status_code == 200
    assert table_from_api == resp.json['table']

    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=table.id),
        json={'changes': [{'context': 'row', 'index': 3, 'label': 'header'}]}
    )
    assert resp.status_code == 200

    resp = client.get(url_for('csv.get_csv_file', csv_id=table.id))
    assert resp.status_code == 200
    assert table_from_api == resp.json['table']


def test_get_csv_file_validation(client, csv_file):
    resp = client.get(
        url_for('csv.get_csv_file_validation', csv_id=csv_file.id)
    )
    assert resp.json == []

    resp = client.put(
        url_for('csv.batch_modify_label', csv_id=csv_file.id),
        json={'changes': [{'context': 'column', 'index': 1, 'label': 'metadata'}]}
    )
    assert resp.status_code == 200

    resp = client.get(
        url_for('csv.get_csv_file_validation', csv_id=csv_file.id)
    )
    assert resp.json == [{
        'context': 'table',
        'severity': 'error',
        'title': 'No group column',
        'type': 'group-missing'
    }]


def test_modify_csv_file_metadata(client, csv_file):
    resp = client.put(
        url_for('csv.set_csv_file_metadata', csv_id=csv_file.id), json={'foo': 'bar'})
    assert resp.status_code == 200
    assert resp.json['meta'] == {'foo': 'bar'}

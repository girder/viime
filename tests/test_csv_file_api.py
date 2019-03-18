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
        'file': (BytesIO(csv_data.encode()), 'test_file1.csv')
    }
    resp = client.post(
        url_for('csv.upload_csv_file'), data=data, content_type='multipart/form-data')

    assert resp.status_code == 201
    assert resp.json['name'] == 'test_file1.csv'
    assert csv_data.strip().startswith('id,col1,col2')
    assert len(resp.json['columns']) == 3


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
    assert resp.json['table'] == csv_file.table.to_csv()


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

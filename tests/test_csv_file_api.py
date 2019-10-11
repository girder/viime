from io import BytesIO

from flask import url_for

from viime.models import CSVFile, CSVFileSchema, db, ValidatedMetaboliteTable

csv_data = """
id,col1,col2
row1,0.5,2.0
row2,1.5,0
"""


def test_upload_csv_file(client):
    data = {
        'file': (BytesIO(csv_data.encode()), 'test_file1.csv', 'text/csv'),
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


def test_get_imputation_options(client, csv_file):
    resp = client.get(
        url_for('csv.set_imputation_options', csv_id=csv_file.id)
    )
    assert resp.status_code == 200
    assert resp.json == {
        'imputation_mnar': csv_file.imputation_mnar,
        'imputation_mcar': csv_file.imputation_mcar
    }


def test_set_imputation_options(client, csv_file):
    resp = client.put(
        url_for('csv.set_imputation_options', csv_id=csv_file.id),
        json={'mnar': 'half-minimum', 'mcar': 'knn'}
    )
    assert resp.status_code == 200
    assert resp.json == {'imputation_mnar': 'half-minimum', 'imputation_mcar': 'knn'}


def test_set_transformation_options(client, csv_file):
    resp = client.post(
        url_for('csv.save_validated_csv_file', csv_id=csv_file.id)
    )
    assert resp.status_code == 201

    resp = client.put(
        url_for('csv.set_transformation_method', csv_id=csv_file.id),
        json={'method': 'log10'}
    )
    assert resp.status_code == 200

    resp = client.get(
        url_for('csv.get_csv_file', csv_id=csv_file.id)
    )
    assert resp.status_code == 200
    assert resp.json['transformation'] == 'log10'


def test_merge_files(client):
    csv_file_schema = CSVFileSchema()
    csv_file1 = csv_file_schema.load({
        'table': 'id,g,col1,col2\nrow1,g,0.5,2.0\nrow2,g,1.5,0\nrow3,h,3,-1.0\n',
        'name': 'test_csv_file1.csv'
    })
    csv_file2 = csv_file_schema.load({
        'table': 'id,g,col3,col4\nrow1,g,0.5,2.0\nrow2,g,1.5,0\nrow4,h,3,-1.0\n',
        'name': 'test_csv_file2.csv'
    })

    db.session.add_all([csv_file1, csv_file2])
    db.session.flush()

    validated1 = ValidatedMetaboliteTable.create_from_csv_file(csv_file1)
    validated2 = ValidatedMetaboliteTable.create_from_csv_file(csv_file2)
    db.session.add_all([validated1, validated2])
    db.session.commit()

    resp = client.post(url_for('csv.merge_csv_files'),
                       json={
                           'name': 'merge',
                           'description': '',
                           'method': 'simple',
                           'datasets': [csv_file1.id, csv_file2.id]
                        })
    assert resp.status_code == 201

    expected_column_types = [{
        'column_header': 'nan',
        'column_index': 0,
        'column_type': 'key'
    }, {
        'column_header': 'g',
        'column_index': 1,
        'column_type': 'group'
    }, {
        'column_header': 'g_1',
        'column_index': 2,
        'column_type': 'group'
    }, {
        'column_header': 'col1',
        'column_index': 3,
        'column_type': 'measurement'
    }, {
        'column_header': 'col2',
        'column_index': 4,
        'column_type': 'measurement'
    }, {
        'column_header': 'col3',
        'column_index': 5,
        'column_type': 'measurement'
    }, {
        'column_header': 'col4',
        'column_index': 6,
        'column_type': 'measurement'
    }]

    expected_row_types = [{
        'row_index': 0,
        'row_name': 'nan',
        'row_type': 'header'
    }, {
        'row_index': 1,
        'row_name': 'Data Source',
        'row_type': 'metadata'
    }, {
        'row_index': 2,
        'row_name': 'row1',
        'row_type': 'sample'
    }, {
        'row_index': 3,
        'row_name': 'row2',
        'row_type': 'sample'
    }]

    assert resp.json['columns'] == expected_column_types
    assert resp.json['rows'] == expected_row_types

    # test remerge which shouldn't change a thing

    resp = client.post(url_for('csv.remerge_csv_file', csv_id=resp.json['id']))
    assert resp.status_code == 200
    assert resp.json['columns'] == expected_column_types
    assert resp.json['rows'] == expected_row_types

from io import BytesIO
import json
from pathlib import Path

from flask import url_for
import pytest


@pytest.fixture(params=['roc.csv', 'plsda/plsda1.csv', 'plsda/plsda2.csv'])
def test_dataset(client, request):
    file = request.param
    with (Path(__file__).parent / file).open('rb') as f:
        csv_data = f.read()
    data = {'file': (BytesIO(csv_data), file, 'text/csv')}
    resp = client.post(
        url_for('csv.upload_csv_file'), data=data, content_type='multipart/form-data')
    assert resp.status_code == 201
    csv_id = resp.json['id']

    if file == 'roc.csv':
        changes = [
            {'context': 'column', 'index': 71, 'label': 'group'},
            {'context': 'column', 'index': 1, 'label': 'measurement'}
        ]
        data = {'changes': changes}
        resp = client.put(url_for('csv.batch_modify_label', csv_id=csv_id), json=data)
        assert resp.status_code == 200

    resp = client.post(url_for('csv.save_validated_csv_file', csv_id=csv_id))
    assert resp.status_code == 201

    yield csv_id, file


def test_roc(client, test_dataset):
    csv_id, filename = test_dataset
    if filename != 'roc.csv':
        return
    data = {
        'group1': 'C',
        'group2': 'H',
        'columns': json.dumps(['5-oxoproline (Pyroglutamic acid)']),
        'method': 'random_forest'
    }
    resp = client.get(url_for('csv.get_roc', csv_id=str(csv_id)), json=data)
    assert resp.status_code == 200
    keys = {'sensitivities', 'thresholds', 'specificities', 'auc'}
    assert keys == set(resp.json.keys())
    for key in keys:
        for value in resp.json[key]:
            assert value in {'Inf', '-Inf'} or 0 <= value <= 1


def test_factor_analysis(client, test_dataset):
    csv_id, filename = test_dataset

    resp = client.get(url_for('csv.get_factors', csv_id=str(csv_id)))
    assert resp.status_code == 200

    eigenvalues = resp.json.get('eigenvalues')
    factors = resp.json.get('factor')
    metabolites = resp.json.get('metabolites')
    variances = resp.json.get('variances')

    assert len(eigenvalues) == len(factors) == len(metabolites) == len(variances)

    for factor in factors:
        assert isinstance(factor, int)

    if filename == 'roc.csv':
        # test factor analysis that fails
        resp = client.get(url_for('csv.get_factors', csv_id=str(csv_id), threshold=0.6))
        assert resp.status_code == 200
        assert 'eigenvalues' not in resp.json
        assert 'factor' not in resp.json
        assert 'metabolites' not in resp.json
        assert 'variances' not in resp.json

def test_plsda(client, test_dataset):
    csv_id, filename = test_dataset

    # Get column and row data
    columns = client.get(url_for('csv.list_columns', csv_id=str(csv_id))).json
    rows = client.get(url_for('csv.list_rows', csv_id=str(csv_id))).json
    columns = [
        column['column_header'] for column in columns if column['column_type'] == 'measurement'
    ]
    rows = [row for row in rows if row['row_type'] == 'sample']

    # perform PLSDA with no `num_of_components` parameter
    data = {}
    resp = client.get(url_for('csv.get_plsda', csv_id=str(csv_id)), json=data)
    assert resp.status_code == 200
    keys = {'scores', 'loadings'}
    assert keys == set(resp.json.keys())

    num_of_components = min(len(columns), len(rows))  # default num_of_components

    loadings = resp.json.get('loadings')
    for loading in loadings:
        assert loading.get('col') in columns
        assert loading.get('loadings') is not None

        assert len(loading.get('loadings')) == num_of_components

    scores = resp.json.get('scores')

    assert 'sdev' in scores.keys()
    assert len(scores.get('sdev')) == num_of_components
    assert 'x' in scores.keys()
    assert len(scores.get('x')) == len(rows)

    for sdev in scores.get('sdev'):
        assert len(sdev) == len(rows)
    for x in scores.get('x'):
        assert len(x) == num_of_components

    # perform PLSDA with `num_of_components` = 10
    num_of_components = 10
    data = {'num_of_components': num_of_components}
    resp = client.get(url_for('csv.get_plsda', csv_id=str(csv_id)), json=data)
    loadings = resp.json.get('loadings')
    for loading in loadings:
        assert loading.get('col') in columns
        assert loading.get('loadings') is not None
        assert len(loading.get('loadings')) == num_of_components

    scores = resp.json.get('scores')

    assert 'sdev' in scores.keys()
    assert len(scores.get('sdev')) == num_of_components
    assert 'x' in scores.keys()
    assert len(scores.get('x')) == len(rows)

    for sdev in scores.get('sdev'):
        assert len(sdev) == len(rows)
    for x in scores.get('x'):
        assert len(x) == num_of_components

    # perform PLSDA with `number_of_components` invalid
    data = {'num_of_components': min(len(columns), len(rows)) + 1}
    resp = client.get(url_for('csv.get_plsda', csv_id=str(csv_id)), json=data)
    assert resp.status_code == 400
    assert 'error' in resp.json

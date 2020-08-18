from io import BytesIO
import json
from pathlib import Path

from flask import url_for
import pytest


@pytest.fixture(params=['roc.csv'])
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

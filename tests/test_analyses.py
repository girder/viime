import json

from flask import url_for


def test_roc(client, test_dataset):
    csv_id = test_dataset
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
    csv_id = test_dataset

    resp = client.get(url_for('csv.get_factors', csv_id=str(csv_id)))
    assert resp.status_code == 200

    eigenvalues = resp.json.get('eigenvalues')
    factors = resp.json.get('factor')
    metabolites = resp.json.get('metabolites')
    variances = resp.json.get('variances')

    assert len(eigenvalues) == len(factors) == len(metabolites) == len(variances)

    for factor in factors:
        assert isinstance(factor, int)

    # test factor analysis that fails
    resp = client.get(url_for('csv.get_factors', csv_id=str(csv_id), threshold=0.6))
    assert resp.status_code == 200
    assert 'eigenvalues' not in resp.json
    assert 'factor' not in resp.json
    assert 'metabolites' not in resp.json
    assert 'variances' not in resp.json

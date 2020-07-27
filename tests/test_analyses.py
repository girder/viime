from io import BytesIO
import json
from pathlib import Path

from flask import url_for


def test_roc(client):
    with (Path(__file__).parent / 'roc.csv').open('rb') as f:
        csv_data = f.read()
    data = {'file': (BytesIO(csv_data), 'roc.csv', 'text/csv')}
    resp = client.post(
        url_for('csv.upload_csv_file'), data=data, content_type='multipart/form-data')
    assert resp.status_code == 201
    csv_id = resp.json['id']

    data = {'changes': [
        {'context': 'column', 'index': 71, 'label': 'group'},
        {'context': 'column', 'index': 1, 'label': 'measurement'}
    ]}
    resp = client.put(url_for('csv.batch_modify_label', csv_id=csv_id), json=data)
    assert resp.status_code == 200

    resp = client.post(url_for('csv.save_validated_csv_file', csv_id=csv_id))
    assert resp.status_code == 201

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

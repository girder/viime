from io import BytesIO

from flask import url_for
import pandas
from pandas.testing import assert_frame_equal

from metabulo.models import db


def test_post_transform(client, csv_file):
    data = {
        'transform_type': 'set_value',
        'row': 'row1',
        'column': 'col1',
        'value': 100,
        'priority': 1
    }
    resp = client.post(url_for('csv.create_transform', csv_id=str(csv_file.id)), json=data)
    assert resp.status_code == 201

    table = pandas.read_csv(
        BytesIO(resp.json['csv_file']['measurement_table'].encode()), header=None)
    assert table.iat[1,1] == 100


def test_delete_transform(client, csv_file):
    t1 = csv_file.generate_transform({
        'transform_type': 'normalize',
        'priority': 1
    })
    db.session.add(t1)
    db.session.commit()

    resp = client.delete(
        url_for('csv.delete_transform', csv_id=str(csv_file.id), transform_id=str(t1.id))
    )
    assert resp.status_code == 204
    assert_frame_equal(csv_file.table, csv_file.measurement_table)

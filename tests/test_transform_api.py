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

    table = pandas.read_csv(BytesIO(resp.json['csv_file']['table'].encode()), index_col=0)
    assert table.at['row1', 'col1'] == 100


def test_delete_transform(client, csv_file):
    t1 = csv_file.generate_transform({
        'transform_type': 'drop_row',
        'row': 'row1',
        'priority': 1
    })
    db.session.add(t1)
    db.session.commit()

    resp = client.delete(
        url_for('csv.delete_transform', csv_id=str(csv_file.id), transform_id=str(t1.id))
    )
    assert resp.status_code == 204
    assert_frame_equal(csv_file.table, csv_file.raw_table)

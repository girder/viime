from io import BytesIO
import math

from flask import url_for
import pandas
from pandas.testing import assert_frame_equal
import pytest

from viime import normalization
from viime import scaling
from viime import transformation
from viime.models import CSVFile, db, ValidatedMetaboliteTable


@pytest.fixture
def table(app):
    with app.app_context():
        yield pandas.read_csv(BytesIO(b"""
id,col1,col2
row1,0.5,2.0
row2,1.5,0.0
"""), index_col=0)


@pytest.fixture
def validated_table(app, csv_file):
    validated_table = ValidatedMetaboliteTable.create_from_csv_file(csv_file)
    db.session.add(validated_table)
    db.session.commit()
    yield validated_table


@pytest.fixture
def column_meta(app):
    with app.app_context():
        yield pandas.read_csv(BytesIO(b"""
id,weight,volume
row1,0.2,24
row2,0.4,40
"""), index_col=0)


def test_normalize_minmax(table):
    correct = table.copy()
    correct[:] = [[0.0, 1.0], [1.0, 0.0]]
    t = normalization.normalize('minmax', table)
    assert_frame_equal(t, correct)


def test_normalize_none(table):
    correct = table.copy()
    t = normalization.normalize(None, table)
    assert_frame_equal(t, correct)


def test_normalize_sum(table):
    correct = table.copy()
    correct[:] = [[200.0, 800.0], [1000.0, 0.0]]
    t = normalization.normalize('sum', table)
    assert_frame_equal(t, correct)


def test_normalize_reference_sample(table):
    correct = table.copy()
    correct[:] = [[0.5, 2.0], [2.5, 0.0]]
    t = normalization.normalize('reference-sample', table, 'row1')
    assert_frame_equal(t, correct)


def test_normalize_weight_volume(table, column_meta):
    meta = column_meta.copy()
    correct = table.copy()
    correct[:] = [[250.0, 1000.0], [375.0, 0.0]]
    t = normalization.normalize('weight-volume', table, 'weight', None, meta)
    assert_frame_equal(t, correct)


def test_normalize_api(client, csv_file, validated_table):
    resp = client.put(
        url_for('csv.set_normalization_method', csv_id=csv_file.id), json={'method': 'minmax'}
    )
    assert resp.status_code == 200
    assert resp.json['normalization'] == 'minmax'
    assert abs(ValidatedMetaboliteTable.query.get(validated_table.id)
               .measurements.iloc[0, 0]) < 1e-8

    resp = client.put(
        url_for('csv.set_normalization_method', csv_id=csv_file.id), json={'method': None}
    )
    assert resp.status_code == 200
    assert resp.json['normalization'] is None
    assert ValidatedMetaboliteTable.query.get(validated_table.id) \
        .measurements.iloc[0, 0] == 0.5


def test_scale_none(table):
    correct = table.copy()
    t = scaling.scale(None, table)
    assert_frame_equal(t, correct)


def test_scale_auto(table):
    t = scaling.scale('auto', table)
    assert abs(t.iloc[0, 0] + math.sqrt(0.5)) < 1e-8


def test_scale_api(client, csv_file, validated_table):
    resp = client.put(
        url_for('csv.set_scaling_method', csv_id=csv_file.id), json={'method': 'auto'}
    )
    assert resp.status_code == 200
    assert resp.json['scaling'] == 'auto'
    assert abs(ValidatedMetaboliteTable.query.get(validated_table.id)
               .measurements.iloc[0, 0] + math.sqrt(0.5)) < 1e-8

    resp = client.put(
        url_for('csv.set_scaling_method', csv_id=csv_file.id), json={'method': None}
    )
    assert resp.status_code == 200
    assert resp.json['scaling'] is None
    assert ValidatedMetaboliteTable.query.get(validated_table.id) \
        .measurements.iloc[0, 0] == 0.5


def test_transform_none(table):
    correct = table.copy()
    t = transformation.transform(None, table)
    assert_frame_equal(t, correct)


def test_transform_log10(table):
    t = transformation.transform('log10', table)
    assert abs(t.iloc[0, 0] - math.log10(0.5)) < 1e-8


def test_transform_api(client, csv_file, validated_table):
    csv_file = CSVFile.query.get(csv_file.id)
    resp = client.put(
        url_for('csv.set_transformation_method', csv_id=csv_file.id), json={'method': 'squareroot'}
    )
    assert resp.status_code == 200
    print(resp.json.keys())
    assert resp.json['transformation'] == 'squareroot'
    assert ValidatedMetaboliteTable.query.get(validated_table.id) \
        .measurements.iloc[0, 0] == math.sqrt(0.5)

    resp = client.put(
        url_for('csv.set_transformation_method', csv_id=csv_file.id), json={'method': None}
    )
    assert resp.status_code == 200
    assert resp.json['transformation'] is None
    assert ValidatedMetaboliteTable.query.get(validated_table.id) \
        .measurements.iloc[0, 0] == 0.5

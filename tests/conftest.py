from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from compare_csv import CSV
import dotenv
from flask import url_for
import pytest

from viime import models
from viime.app import create_app
from viime.models import CSVFileSchema, db, ValidatedMetaboliteTable


csv_file_schema = CSVFileSchema()
pathological_file_path = Path(__file__).parent / 'pathological.csv'


@pytest.fixture(autouse=True)
def mock_load_dotenv(monkeypatch):
    def do_nothing(*args, **kwargs):
        pass

    monkeypatch.setattr(dotenv, 'load_dotenv', do_nothing)


@pytest.fixture(autouse=True)
def mock_imputation(monkeypatch):
    def noop(table, groups, **kwargs):
        return table.copy(), dict(mnar=[], mcar=[])

    monkeypatch.setattr(models, 'impute_missing', noop)


@pytest.fixture
def app():
    with TemporaryDirectory() as upload_folder:
        app = create_app({
            'ENV': 'testing',
            'SQLALCHEMY_DATABASE_URI': 'sqlite://',
            'UPLOAD_FOLDER': upload_folder,
            'OPENCPU_API_ROOT': 'http://localhost:8004/ocpu/library'
        })

        with app.app_context():
            db.create_all()

        yield app


@pytest.fixture
def client(app):
    with app.test_request_context(), app.test_client() as client:
        yield client


@pytest.fixture
def csv_file(client):
    csv_file = csv_file_schema.load({
        'table': 'id,g,col1,col2\nrow1,g,0.5,2.0\nrow2,g,1.5,0\n',
        'name': 'test_csv_file.csv'
    })
    db.session.add(csv_file)
    db.session.commit()
    yield csv_file


@pytest.fixture
def validated_csv_file(client, csv_file):
    db.session.add(ValidatedMetaboliteTable.create_from_csv_file(csv_file))
    db.session.commit()
    yield csv_file


@pytest.fixture
def pathological_table(client):
    with open(pathological_file_path) as f:
        csv_file = csv_file_schema.load({
            'table': f.read(),
            'name': 'pathological.csv'
        })
    db.session.add(csv_file)
    db.session.commit()
    yield csv_file


def pytest_assertrepr_compare(op, left, right):
    if op == '==' and isinstance(left, CSV) and isinstance(right, CSV):
        return left.get_pytest_error(right)


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

    yield csv_id

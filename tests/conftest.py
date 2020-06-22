from pathlib import Path
from tempfile import TemporaryDirectory

from compare_csv import CSV
import dotenv
import pytest

from viime import models
from viime.app import create_app
from viime.models import CSVFileSchema, db


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

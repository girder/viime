from tempfile import NamedTemporaryFile, TemporaryDirectory

import dotenv
import pytest

from metabulo.app import create_app
from metabulo.models import CreateCSVFileSchema, CSVFileSchema, db

create_csv_file_schema = CreateCSVFileSchema()
csv_file_schema = CSVFileSchema()


@pytest.fixture(autouse=True)
def mock_load_dotenv(monkeypatch):
    def do_nothing(*args, **kwargs):
        pass

    monkeypatch.setattr(dotenv, 'load_dotenv', do_nothing)


@pytest.fixture
def app():
    with NamedTemporaryFile() as db_file, TemporaryDirectory() as upload_folder:
        app = create_app({
            'ENV': 'testing',
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_file.name}',
            'UPLOAD_FOLDER': upload_folder
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
    csv_file_args = create_csv_file_schema.load({
        'table': 'id,col1,col2\nrow1,0.5,2.0\nrow2,1.5,0\n',
        'name': 'test_csv_file.csv'
    })
    with open(csv_file_args['uri'], 'w') as f:
        f.write(csv_file_args['table'])

    csv_file = csv_file_schema.load(csv_file_args)
    db.session.add(csv_file)
    db.session.commit()
    yield csv_file

import contextlib
from pathlib import Path
import socket
from tempfile import TemporaryDirectory

import dotenv
import pytest

from viime import models
from viime.app import create_app
from viime.models import CSVFileSchema, db

csv_file_schema = CSVFileSchema()
pathological_file_path = Path(__file__).parent / 'pathological.csv'
dockerfile = str((Path(__file__).parent / '../devops').resolve())


@pytest.fixture(autouse=True)
def mock_load_dotenv(monkeypatch):
    def do_nothing(*args, **kwargs):
        pass

    monkeypatch.setattr(dotenv, 'load_dotenv', do_nothing)


@pytest.fixture(autouse=True)
def mock_imputation(monkeypatch):
    def noop(table, groups, **kwargs):
        return table.copy()

    monkeypatch.setattr(models, 'impute_missing', noop)


@pytest.fixture
def app():
    with TemporaryDirectory() as upload_folder:
        app = create_app({
            'ENV': 'testing',
            'SQLALCHEMY_DATABASE_URI': f'sqlite://',
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


def _find_free_port():
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(('', 0))
        return sock.getsockname()[1]


@pytest.fixture
def opencpu_request(app):
    import docker
    from time import sleep
    from viime.opencpu import opencpu_request

    client = docker.from_env()
    client.images.build(path=dockerfile, tag='viime')
    port = _find_free_port()
    container = client.containers.create('viime', ports={
        '8004/tcp': port})

    app.config['OPENCPU_API_ROOT'] = 'http://localhost:%s/ocpu/library' % port

    container.start()
    sleep(5)

    yield opencpu_request

    container.stop()
    container.remove()

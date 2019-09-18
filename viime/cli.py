import click
import flask_migrate

from viime.app import create_app
from viime.models import db


@click.command()
def create_tables():
    app = create_app()

    with app.app_context():
        db.create_all()
        flask_migrate.stamp()

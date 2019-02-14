import click

from metabulo.app import create_app
from metabulo.models import db


@click.command()
def create_tables():
    app = create_app()

    with app.app_context():
        db.create_all()

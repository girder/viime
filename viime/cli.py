import json
import os
from pathlib import Path, PurePath
from typing import Any, Callable, List, Optional

import click
import flask_migrate
import requests

from viime import samples
from viime.app import create_app
from viime.models import CSVFile, db


samples_dir = str(PurePath(__file__).parent.parent / 'samples')
api_prefix = '/api/v1/sample/sample'


@click.group()
def cli():
    pass


@cli.command(help='initializes the db')
def create_tables():
    app = create_app()

    with app.app_context():
        db.create_all()
        flask_migrate.stamp()


@cli.command(help='load samples into the db')
@click.option('--url', default='http://localhost:8080', show_default=True,
              help='VIIME instance to load into')
@click.option('--local', is_flag=True, help='instead of the url use the local instance')
@click.option('--dir', default=samples_dir, show_default=True, help='samples directory')
@click.argument('ids', nargs=-1)
def load_samples(url: str, dir: str, local: bool = False, ids: Optional[List[str]] = None):
    out_dir = Path(dir)
    os.makedirs(out_dir, exist_ok=True)

    def load_samples(set_data: Callable[[Any], Any]):
        files = [out_dir / f'{id}.json' for id in ids] if ids else out_dir.glob('*.json')
        for fname in files:
            with open(fname, 'r') as f:
                data = json.load(f)
                click.echo(f'importing {fname}')
                set_data(data)
                click.echo(f'imported {fname}')

    if local:
        with create_app().app_context():
            load_samples(lambda data: samples.upload(data))
            db.session.commit()
    else:
        click.echo(f'pushing to: {url}{api_prefix}')
        load_samples(lambda data: requests.post(f'{url}{api_prefix}', json=data).raise_for_status())


@cli.command(help='dump samples from the db')
@click.option('--url', default='https://viime.org', show_default=True,
              help='VIIME instance to dump from')
@click.option('--local', is_flag=True, help='instead of the url use the local instance')
@click.option('--dir', default=samples_dir, show_default=True, help='samples directory')
@click.argument('ids', nargs=-1)
def dump_samples(url: str, dir: str, local: bool = False, ids: Optional[List[str]] = None):
    out_dir = PurePath(dir)
    os.makedirs(out_dir, exist_ok=True)

    def dump_samples(groups: List[Any], get_data: Callable[[str], Any]):
        for group in groups:
            for sample in group['files']:
                fid = sample['id']
                fname = sample['name']
                data = get_data(fid)
                with open(out_dir / f'{fid}.json', 'w') as f:
                    json.dump(data, f, indent=2)
                click.echo(f'dumped {fid} {fname}')

    arg_ids = [dict(files=[dict(id=id, name=id) for id in ids])] if ids else []

    if local:
        with create_app().app_context():
            groups = samples.list_samples() if not ids else arg_ids
            dump_samples(groups, lambda fid: samples.dump(CSVFile.query.get(fid)))
    else:
        click.echo(f'requesting: {url}{api_prefix}')
        groups = requests.get(f'{url}{api_prefix}').json() if not ids else arg_ids
        dump_samples(groups, lambda fid: requests.get(f'{url}{api_prefix}/{fid}').json())


@cli.command(help='mark a list of dataset ids to be samples')
@click.option('--url', default='http://localhost:8080', show_default=True,
              help='VIIME instance')
@click.option('--local', is_flag=True, help='instead of the url use the local instance')
@click.option('--group', default='Default', show_default=True, help='sample group name')
@click.option('--description', default=None, show_default=True, help='sample group description')
@click.argument('ids', nargs=-1)
def mark_sample(url: str, group: str, description: Optional[str], ids: List[str],
                local: bool = False):
    if local:
        with create_app().app_context():
            for id in ids:
                csv = samples.enable_sample(CSVFile.query.get(id), group, description)
                db.session.add(csv)
            db.session.commit()
    else:
        click.echo(f'using: {url}{api_prefix}')
        for id in ids:
            data = dict(group=group, description=description)
            requests.put(f'{url}{api_prefix}/{id}', json=data).raise_for_status()


@cli.command(help='unmark a list of dataset ids to be samples')
@click.option('--url', default='http://localhost:8080', show_default=True,
              help='VIIME instance')
@click.option('--local', is_flag=True, help='instead of the url use the local instance')
@click.argument('ids', nargs=-1)
def unmark_sample(url: str, ids: List[str], local: bool = False):
    if local:
        with create_app().app_context():
            for id in ids:
                csv = samples.disable_sample(CSVFile.query.get(id))
                db.session.add(csv)
            db.session.commit()
    else:
        click.echo(f'using: {url}{api_prefix}')
        for id in ids:
            requests.delete(f'{url}{api_prefix}/{id}').raise_for_status()

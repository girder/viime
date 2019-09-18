from distutils import log
import os

from setuptools import find_packages, setup


def list_files_recursive(relpath):
    for root, dirs, files in os.walk(relpath):
        install_root = os.path.join('share', 'metabulo', root)
        yield install_root, [os.path.join(root, file) for file in files]


if not os.path.exists(os.path.join('static', 'index.html')):
    log.warn(
        'Static assets are not built.  Run "npm install && npm run build" '
        'in the web directory prior to packaging metabulo.'
    )

data_files = []
data_files.extend(list_files_recursive('migrations'))
data_files.extend(list_files_recursive('static'))


setup(
    name='metabulo',
    version='0.1.0',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    packages=find_packages(include=['metabulo']),
    include_package_data=True,
    install_requires=[
        'alembic',
        'dogpile.cache',
        'flask',
        'flask-migrate',
        'flask-sqlalchemy',
        'marshmallow==3.0.0rc6',
        'matplotlib',
        'pandas<0.25.0',
        'python-dotenv',
        'requests',
        'sklearn',
        'sqlalchemy-utils',
        'webargs',
        'Werkzeug>=0.15',
        'xlrd>= 1.0.0'
    ],
    extras_require={
        'memcached': ['pylibmc'],
        'sentry': ['sentry-sdk[flask]']
    },
    license='Apache Software License 2.0',
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'metabulo-create-tables=metabulo.cli:create_tables'
        ],
        'dogpile.cache': [
            'flask_request_local = metabulo.cache:FlaskRequestLocalBackend'
        ]
    }
)

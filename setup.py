from distutils import log
import os

from setuptools import find_packages, setup


def list_files_recursive(relpath):
    for root, dirs, files in os.walk(relpath):
        install_root = os.path.join('share', 'viime', root)
        yield install_root, [os.path.join(root, file) for file in files]


if not os.path.exists(os.path.join('static', 'index.html')):
    log.warn(
        'Static assets are not built.  Run "npm install && npm run build" '
        'in the web directory prior to packaging viime.'
    )

data_files = []
data_files.extend(list_files_recursive('migrations'))
data_files.extend(list_files_recursive('static'))


setup(
    name='viime',
    version='1.0.1',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    packages=find_packages(include=['viime']),
    include_package_data=True,
    install_requires=[
        'alembic',
        'dogpile.cache',
        'flask',
        'flask-cors',
        'flask-migrate',
        'flask-sqlalchemy',
        'marshmallow>=3.0.0',
        'matplotlib',
        'pandas>=0.25.0',
        'python-dotenv',
        'requests',
        'sklearn',
        'sqlalchemy-utils',
        'webargs >=5.5.3, <6',
        'Werkzeug>=0.15',
        'xlrd>= 1.0.0'
    ],
    extras_require={
        'memcached': ['pylibmc'],
        'sentry': ['sentry-sdk[flask]>=0.13']
    },
    license='Apache Software License 2.0',
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'viime-cli=viime.cli:cli'
        ],
        'dogpile.cache': [
            'flask_request_local = viime.cache:FlaskRequestLocalBackend'
        ]
    }
)

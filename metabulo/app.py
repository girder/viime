import os

from dotenv import load_dotenv
from flask import current_app, Flask, jsonify
from marshmallow import ValidationError
from werkzeug.middleware.proxy_fix import ProxyFix

from metabulo.cache import clear_cache, persistent_region
from metabulo.models import db
from metabulo.opencpu import OpenCPUException
from metabulo.views import csv_bp

try:
    import pylibmc
except ImportError:
    pylibmc = None


def handle_validation_error(e):
    return jsonify(e.messages), 400


def handle_opencpu_error(e):
    return e.error_response


def handle_general_error(e):
    current_app.logger.exception(e)
    return jsonify({'error': 'Something went wrong.'}), 500


def create_app(config=None):
    load_dotenv(os.getenv('DOTENV_PATH'))

    config = config or {}
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_UPLOAD_SIZE', 5 * 1024 * 1024))
    app.config['OPENCPU_API_ROOT'] = os.getenv('OPENCPU_API_ROOT')

    app.config.update(config)
    db.init_app(app)

    app.register_blueprint(csv_bp, url_prefix='/api/v1')

    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(OpenCPUException, handle_opencpu_error)
    if app.config['ENV'] == 'production':
        app.register_error_handler(500, handle_general_error)

    if 'MEMCACHED_URI' in os.environ and pylibmc:
        persistent_region.configure(
            'dogpile.cache.pylibmc',
            arguments={
                'url': os.environ['MEMCACHED_URI'],
                'binary': True
            },
            replace_existing_backend=True
        )

    @app.after_request
    def clear_cache_after_request(response):
        clear_cache()
        return response

    return app

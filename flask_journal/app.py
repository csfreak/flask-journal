from flask import Flask
from flask.config import Config as FlaskConfig
from werkzeug.middleware.proxy_fix import ProxyFix

from . import config


def create_app(c: FlaskConfig | None = None) -> Flask:
    app: Flask = Flask('flask-journal')
    if c is None:
        c = config.load_config()
    app.config.from_mapping(c)

    from .models import db, init_db  # noqa F401
    init_db(app)

    if app.config.get('IS_GUNICORN'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_port=1, x_proto=1, x_host=1)

        from .metrics import metrics

        metrics.init_app(app)

    return app

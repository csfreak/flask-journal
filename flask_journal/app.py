from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config


def create_app(c: Config | None = None) -> Flask:
    app: Flask = Flask('flask-journal')
    if c is None:
        c = Config()
    app.config.from_object(c)
    if not app.testing:
        app.config.from_prefixed_env("JOURNAL")

    for k, v in app.config.items():
        app.logger.debug("Setting %s has %s", k, v)

    from .models import db, init_db  # noqa F401
    init_db(app)

    from .security import init_security
    init_security(app)

    if app.config.get('IS_GUNICORN'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2,
                                x_port=1, x_proto=1, x_host=1)

        from .metrics import metrics

        metrics.init_app(app)

    return app

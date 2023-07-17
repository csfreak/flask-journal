import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Config, init_config


def create_app(c: Config | None = None) -> Flask:
    app: Flask = Flask('flask-journal',
                       root_path=os.getenv('FLASK_ROOT_PATH', None))
    init_config(app, c)

    from .models import db, init_db  # noqa F401
    init_db(app)

    from .security import init_security
    init_security(app)

    from .views import init_views
    init_views(app)

    if app.config.get('IS_GUNICORN'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2,
                                x_port=1, x_proto=1, x_host=1)

        from .metrics import metrics

        metrics.init_app(app)

    return app

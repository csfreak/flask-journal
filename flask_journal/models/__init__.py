from flask import Flask
from flask_migrate import Migrate, upgrade

from .db import db
from .entry import Entry  # noqa: F401
from .rbac import Role  # noqa: F401
from .tag import Tag  # noqa: F401
from .user import User, UserSettings  # noqa: F401

migrate = Migrate()


def init_db(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        upgrade()

from flask import Flask
from flask_alembic import Alembic

from .db import db

alembic = Alembic()


def init_db(app: Flask) -> None:
    db.init_app(app)
    alembic.init_app(app)

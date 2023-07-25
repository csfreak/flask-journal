import typing as t

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class TestSmoke:
    def test_app_instance(self: t.Self, app: Flask) -> None:
        assert isinstance(app, Flask)

    def test_app_config(self: t.Self, app: Flask) -> None:
        assert app.config["TESTING"]

    def test_db_type(self: t.Self, db: SQLAlchemy) -> None:
        assert isinstance(db, SQLAlchemy)

    def test_db_instance(self: t.Self, app: Flask, db: SQLAlchemy) -> None:
        assert db is app.extensions["sqlalchemy"]

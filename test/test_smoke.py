from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def test_app_instance(app: Flask) -> None:
    assert isinstance(app, Flask)


def test_app_config(app: Flask) -> None:
    assert app.config["TESTING"]


def test_db_type(db: SQLAlchemy) -> None:
    assert isinstance(db, SQLAlchemy)


def test_db_instance(app: Flask, db: SQLAlchemy) -> None:
    assert db is app.extensions["sqlalchemy"]

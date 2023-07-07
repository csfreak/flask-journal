import typing as t

import flask_unittest
from flask import Flask

from flask_journal.app import create_app
from flask_journal.config import load_mapping
from flask_journal.models import db

env = {
    "SECURITY_EMAIL_VALIDATOR_ARGS": '{"check_deliverability": False}',
    "SECURITY_PASSWORD_HASH": "plaintext",
    "SQLALCHEMY_DATABASE_URI": "sqlite://",
    "TESTING": True
}


class AppTestBase(flask_unittest.AppTestCase):

    def create_app(self: t.Self) -> t.Generator[Flask, t.Any, t.Any]:
        """Create and configure a new app instance for each test."""
        app = create_app(load_mapping(env))

        with app.app_context():
            yield app

    def setUp(self: t.Self, app: Flask) -> None:
        db.create_all()

    def tearDown(self: t.Self, app: Flask) -> None:
        db.drop_all()
        db.drop_all()

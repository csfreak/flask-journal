import typing as t

import flask_unittest
from flask import Flask

from flask_journal.app import create_app
from flask_journal.config import Config
from flask_journal.models import db

test_config = {
    "SECURITY_EMAIL_VALIDATOR_ARGS": {"test_environment": True},
    "SECURITY_PASSWORD_HASH": "plaintext",
    "SQLALCHEMY_DATABASE_URI": "sqlite://",
    "TESTING": True,
    "WTF_CSRF_ENABLED": False,

}


class AppTestBase(flask_unittest.AppTestCase):

    def create_app(self: t.Self) -> t.Generator[Flask, t.Any, t.Any]:
        """Create and configure a new app instance for each test."""
        app = create_app(Config(mapping=test_config))

        with app.app_context():
            yield app

    def setUp(self: t.Self, app: Flask) -> None:
        db.create_all()

    def tearDown(self: t.Self, app: Flask) -> None:
        db.drop_all()

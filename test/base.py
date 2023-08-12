import typing as t

import flask_unittest
from flask import Flask

from flask_journal.app import create_app
from flask_journal.config import Config
from flask_journal.models import db
from flask_journal.models.setup import init_data

from .config import test_config


class AppTestBase(flask_unittest.AppTestCase):
    def create_app(self: t.Self) -> t.Generator[Flask, t.Any, t.Any]:
        """Create and configure a new app instance for each test."""
        app = create_app(Config(mapping=test_config))

        with app.app_context():
            yield app

    def setUp(self: t.Self, app: Flask) -> None:
        db.create_all()
        init_data(app)

    def tearDown(self: t.Self, app: Flask) -> None:
        db.drop_all()

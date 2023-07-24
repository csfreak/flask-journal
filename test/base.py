import typing as t
from datetime import datetime

import flask_unittest
from flask import Flask
from flask.testing import FlaskClient

from flask_journal.app import create_app
from flask_journal.config import Config
from flask_journal.models import UserSettings, db
from flask_journal.models.setup import init_data
from flask_journal.security import security

from .config import security_config, test_config


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


class AppClientTestBase(flask_unittest.AppClientTestCase):
    def create_app(self: t.Self) -> t.Generator[Flask, t.Any, t.Any]:
        """Create and configure a new app instance for each test."""
        app = create_app(Config(mapping=test_config))

        with app.app_context():
            yield app

    def setUp(self: t.Self, app: Flask, client: FlaskClient) -> None:
        db.create_all()
        init_data(app)
        for user in security_config["users"]:
            enorm = security._mail_util.validate(user["email"])
            pbad, pnorm = security._password_util.validate(user["password"], True)

            security.datastore.create_user(
                email=enorm,
                password=pnorm,
                active=user["active"],
                confirmed_at=datetime.now(),
                settings=UserSettings(),
            )
            u = security.datastore.find_user(email=user["email"])

            db.session.add(u)

            for role in user["roles"]:
                security.datastore.add_role_to_user(u, role)
        db.session.commit()
        return super().setUp(app, client)

    def tearDown(self: t.Self, app: Flask, client: FlaskClient) -> None:
        client.delete_cookie("session")
        db.drop_all()
        return super().tearDown(app, client)


class UserAppTestBase(AppTestBase):
    def setUp(self: t.Self, app: Flask) -> None:
        super().setUp(app)
        for user in security_config["users"]:
            enorm = security._mail_util.validate(user["email"])
            pbad, pnorm = security._password_util.validate(user["password"], True)

            security.datastore.create_user(
                email=enorm,
                password=pnorm,
                active=user["active"],
                confirmed_at=datetime.now(),
                settings=UserSettings(),
            )
            u = security.datastore.find_user(email=user["email"])
            db.session.add(u)

            for role in user["roles"]:
                security.datastore.add_role_to_user(u, role)
        db.session.commit()

    def tearDown(self: t.Self, app: Flask) -> None:
        return super().tearDown(app)

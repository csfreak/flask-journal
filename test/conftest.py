import logging
from datetime import datetime

import pytest
from flask import Flask, g
from flask.testing import FlaskClient
from flask_security import AnonymousUser, datastore
from flask_sqlalchemy import SQLAlchemy

from flask_journal.app import create_app
from flask_journal.config import Config
from flask_journal.models import User, UserSettings
from flask_journal.models import db as db_extension
from flask_journal.security import security

from .config import security_config, test_config

logger = logging.getLogger(__name__)


@pytest.fixture
def app() -> Flask:
    logger.debug("Initialize App")
    app = create_app(Config(mapping=test_config))

    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    logger.debug("Initialize Client")
    with app.test_client() as client:
        yield client


@pytest.fixture
def db(app: Flask) -> SQLAlchemy:
    logger.debug("Initialize DB")
    db_extension.create_all()
    yield db_extension
    logger.debug("TearDown DB")
    db_extension.drop_all()


@pytest.fixture
def userdatastore(app: Flask, db: SQLAlchemy) -> datastore:
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
        u: User = security.datastore.find_user(email=user["email"])
        db.session.add(u)

        for role in user["roles"]:
            security.datastore.add_role_to_user(u, role)
    db.session.commit()
    return security.datastore


@pytest.fixture(params=[user["email"] for user in security_config["users"]])
def user(userdatastore: datastore, request: pytest.FixtureRequest) -> User:
    return userdatastore.find_user(email=request.param)


@pytest.fixture
def logged_in_user_context(
    app: Flask, userdatastore: datastore, request: pytest.FixtureRequest
) -> None:
    with app.test_request_context():
        u: User = userdatastore.find_user(email=request.param)
        if u is None:
            u = AnonymousUser()
        g._login_user = u
        yield None


@pytest.fixture
def logged_in_user_client(
    client: FlaskClient, userdatastore: datastore, request: pytest.FixtureRequest
) -> FlaskClient:
    client.get("/auth/login")
    for user in security_config["users"]:
        if user["email"] == request.param:
            client.post(
                "/auth/login",
                data={"email": user["email"], "password": user["password"]},
            )
            break
    else:
        raise ValueError("email not found in security config: %s" % request.email)
    yield client
    client.get("/auth/logout")
    client.delete_cookie("session")

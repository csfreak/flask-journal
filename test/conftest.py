import logging
from datetime import datetime
from typing import Generator

import pytest
from flask import Flask, g
from flask.testing import FlaskClient
from flask_security.datastore import UserDatastore
from flask_sqlalchemy import SQLAlchemy

from flask_journal.app import create_app
from flask_journal.config import Config
from flask_journal.models import User, UserSettings
from flask_journal.models import db as db_extension
from flask_journal.models.setup import init_data
from flask_journal.security import security

from .config import security_config, test_config

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def app() -> Generator[Flask, None, None]:
    logger.debug("Initialize App")
    app = create_app(Config(mapping=test_config))

    with app.app_context():
        yield app
    logger.debug("Teardown App")
    del app


@pytest.fixture
def client(app: Flask) -> Generator[FlaskClient, None, None]:
    logger.debug("Initialize Client")
    with app.test_client() as client:
        yield client
    logger.debug("Teardown Client")


@pytest.fixture(scope="function")
def db(app: Flask) -> Generator[SQLAlchemy, None, None]:
    logger.debug("Initialize DB")
    init_data(app)
    yield db_extension
    logger.debug("TearDown DB")
    db_extension.drop_all()
    db_extension.session.remove()


@pytest.fixture
def userdatastore(app: Flask, db: SQLAlchemy) -> Generator[UserDatastore, None, None]:
    logger.debug("Initialize userdatastore")
    for user in security_config["users"]:
        enorm = security._mail_util.validate(user["email"])
        pbad, pnorm = security._password_util.validate(user["password"], True)
        logger.debug("Add user %s", enorm)
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
    yield security.datastore


@pytest.fixture(
    params=["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin-user", "manage-user", "base-user"],
)
def user(userdatastore: UserDatastore, request: pytest.FixtureRequest) -> User:
    return userdatastore.find_user(email=request.param)


@pytest.fixture
def logged_in_user_context(app: Flask, user: User) -> Generator[None, None, None]:
    with app.test_request_context():
        logger.debug("Push new request_context with user %s logged in", user)
        g._login_user = user
        yield None
        g._login_user = None


@pytest.fixture
def logged_in_user_client(
    client: FlaskClient, user: User
) -> Generator[FlaskClient, None, None]:
    client.get("/auth/login")
    if user:
        client.post(
            "/auth/login",
            data={
                "email": user.email,
                "password": user.password,
            },
        )
    else:
        raise ValueError("user not found: %s" % user)
    logger.debug("Client logged in as %s", user)
    yield client
    client.get("/auth/logout")
    logger.debug("Client %s logged out", user)
    client.delete_cookie("session")

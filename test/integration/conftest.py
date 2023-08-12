import pytest
from flask import Flask
from flask_security import datastore
from flask_sqlalchemy import SQLAlchemy

from flask_journal.security import security

from ..config import security_config


@pytest.fixture
def outbox(app: Flask) -> list:
    app.extensions["mailman"].outbox = []
    yield app.extensions["mailman"].outbox
    app.extensions["mailman"].outbox = []


@pytest.fixture
def emptydatastore(app: Flask, db: SQLAlchemy) -> datastore:
    yield security.datastore


@pytest.fixture(
    params=security_config["users"],
    ids=[user["email"] for user in security_config["users"]],
)
def user_config(request: pytest.FixtureRequest) -> dict:
    return request.param


@pytest.fixture(
    params=security_config["roles"],
    ids=[user["name"] for user in security_config["roles"]],
)
def role_config(request: pytest.FixtureRequest) -> dict:
    return request.param

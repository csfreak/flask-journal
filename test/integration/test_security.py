from datetime import datetime

import pytest
from flask import Flask, url_for
from flask.testing import FlaskClient
from flask_security import datastore
from flask_security.forms import ConfirmRegisterForm
from flask_security.recoverable import generate_reset_password_token
from flask_security.registerable import register_user
from flask_security.utils import verify_and_update_password

from flask_journal.models import Role as SecurityRole
from flask_journal.models import User as SecurityUser
from flask_journal.models import UserSettings
from flask_journal.security import security
from flask_journal.security.signals import user_init

from ..config import html_test_strings


def test_app_security_instance(app: Flask) -> None:
    assert security == app.extensions["security"]


def test_datastore_create_user(emptydatastore: datastore, user_config: dict) -> None:
    enorm = security._mail_util.validate(user_config["email"])
    pbad, pnorm = security._password_util.validate(user_config["password"], True)

    assert pbad is None

    u: SecurityUser = emptydatastore.create_user(
        email=enorm, password=pnorm, active=user_config["active"]
    )
    assert isinstance(u, SecurityUser)
    assert u.active == user_config["active"]
    assert verify_and_update_password(user_config["password"], u)


def test_datastore_register_user(
    app: Flask, outbox: list, user_config: dict, emptydatastore: datastore
) -> None:
    with app.test_request_context("/auth/register"):
        register_user(
            ConfirmRegisterForm(
                data=dict(email=user_config["email"], password=user_config["password"])
            )
        )

    assert len(outbox) == 1
    assert user_config["email"] in outbox[0].to
    u = emptydatastore.find_user(email=user_config["email"])
    assert isinstance(u, SecurityUser)
    assert u.active
    assert emptydatastore.find_role("user") in u.roles


def test_datastore_create_role(
    emptydatastore: datastore,
    role_config: dict,
) -> None:
    security.datastore.create_role(**role_config)
    r = emptydatastore.find_role(role_config["name"])
    assert isinstance(r, SecurityRole)
    assert r.name == role_config["name"]


def test_user_has_role(emptydatastore: datastore, user_config: dict) -> None:
    enorm = security._mail_util.validate(user_config["email"])
    pbad, pnorm = security._password_util.validate(user_config["password"], True)

    u: SecurityUser = emptydatastore.create_user(
        email=enorm, password=pnorm, active=user_config["active"]
    )

    for role in user_config["roles"]:
        emptydatastore.add_role_to_user(u, role)

    assert user_config["roles"] == [r.name for r in u.roles]

    for role in user_config["roles"]:
        assert u.has_role(role)


def test_user_missing_role(emptydatastore: datastore, user_config: dict) -> None:
    enorm = security._mail_util.validate(user_config["email"])
    pbad, pnorm = security._password_util.validate(user_config["password"], True)

    u: SecurityUser = emptydatastore.create_user(
        email=enorm, password=pnorm, active=user_config["active"]
    )

    assert not u.has_role("testing")


def test_user_login(
    userdatastore: datastore, client: FlaskClient, user_config: dict
) -> None:
    client.get("/auth/login")
    rv = client.post(
        "/auth/login",
        data={"email": user_config["email"], "password": user_config["password"]},
    )
    if user_config["active"]:
        assert rv.status_code == 302
        assert rv.headers["location"] == "/"
        client.post("/auth/logout")
    else:
        assert rv.status_code == 200
        assert html_test_strings["title"] % "Login" in rv.text
    client.delete_cookie("session")


def test_user_login_invalid_password(
    userdatastore: datastore, client: FlaskClient, user_config: dict
) -> None:
    rv = client.post(
        url_for("security.login"),
        data={
            "email": user_config["email"],
            "password": "invalidpassword",
        },
    )
    assert html_test_strings["security"]["error"]["generic"] in rv.text
    assert html_test_strings["title"] % "Login" in rv.text


def test_user_login_not_confirmed(
    emptydatastore: datastore, client: FlaskClient, user_config: dict
) -> None:
    enorm = security._mail_util.validate(user_config["email"])
    pbad, pnorm = security._password_util.validate(user_config["password"], True)

    security.datastore.create_user(
        email=enorm, password=pnorm, active=user_config["active"]
    )

    rv = client.post(
        url_for("security.login"),
        data={
            "email": user_config["email"],
            "password": user_config["password"],
        },
    )
    assert html_test_strings["security"]["error"]["generic"] in rv.text
    assert html_test_strings["title"] % "Login" in rv.text


def test_user_login_non_existent(
    client: FlaskClient, emptydatastore: datastore
) -> None:
    rv = client.post(
        url_for("security.login"),
        data={
            "email": "baduser@example.test",
            "password": "password",
        },
    )
    assert html_test_strings["security"]["error"]["generic"] in rv.text
    assert html_test_strings["title"] % "Login" in rv.text


def test_user_login_invalid_email(
    client: FlaskClient, emptydatastore: datastore
) -> None:
    rv = client.post(
        url_for("security.login"),
        data={
            "email": "notanemailaddress&1",
            "password": "password",
        },
    )
    assert html_test_strings["security"]["error"]["generic"] in rv.text
    assert html_test_strings["title"] % "Login" in rv.text


@pytest.mark.parametrize("endpoint", ["login", "register", "forgot_password"])
def test_context_processors(client: FlaskClient, endpoint: str) -> None:
    title: str = endpoint.replace("_", " ").title()
    rv = client.get(url_for(f"security.{endpoint}"))
    assert html_test_strings["title"] % title in rv.text


def test_context_processor_reset_password(
    client: FlaskClient, user: SecurityUser
) -> None:
    rv = client.get(
        url_for("security.reset_password", token=generate_reset_password_token(user))
    )
    assert html_test_strings["title"] % "Reset Password" in rv.text


def test_user_init_handler(app: Flask, emptydatastore: datastore) -> None:
    enorm = security._mail_util.validate("test@example.test")
    pbad, pnorm = security._password_util.validate("password", True)

    u: SecurityUser = emptydatastore.create_user(
        email=enorm,
        password=pnorm,
        active=True,
        confirmed_at=datetime.now(),
    )

    user_init(app, u)

    assert u.settings is not None
    assert u.has_role("user")


def test_user_init_handler_no_user(app: Flask, emptydatastore: datastore) -> None:
    enorm = security._mail_util.validate("test@example.test")
    pbad, pnorm = security._password_util.validate("password", True)

    u: SecurityUser = emptydatastore.create_user(
        email=enorm,
        password=pnorm,
        active=True,
        confirmed_at=datetime.now(),
    )

    user_init(app, None)

    assert u.settings is None
    assert not u.has_role("user")


def test_user_init_handler_existing_settings(
    app: Flask, emptydatastore: datastore
) -> None:
    enorm = security._mail_util.validate("test@example.test")
    pbad, pnorm = security._password_util.validate("password", True)

    u: SecurityUser = emptydatastore.create_user(
        email=enorm,
        password=pnorm,
        active=True,
        confirmed_at=datetime.now(),
    )

    us = UserSettings()
    u.settings = us
    user_init(app, u)

    assert u.settings is us
    assert u.has_role("user")


def test_user_init_handler_existing_role(app: Flask, emptydatastore: datastore) -> None:
    enorm = security._mail_util.validate("test@example.test")
    pbad, pnorm = security._password_util.validate("password", True)

    u: SecurityUser = emptydatastore.create_user(
        email=enorm,
        password=pnorm,
        active=True,
        confirmed_at=datetime.now(),
    )

    emptydatastore.add_role_to_user(u, "user")
    user_init(app, u)

    assert u.settings is not None
    assert u.has_role("user")

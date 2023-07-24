from flask import g, has_request_context
from flask.testing import FlaskClient
from flask_login.mixins import AnonymousUserMixin as AnonymousUser
from flask_security import UserMixin

from flask_journal.models import User

from .config import security_config


def authenticate(client: FlaskClient, email: str) -> None:
    client.get("/auth/logout")
    client.delete_cookie("session")
    client.get("/auth/login")
    for user in security_config["users"]:
        if user["email"] == email:
            client.post(
                "/auth/login",
                data={"email": user["email"], "password": user["password"]},
            )
            break
    else:
        raise ValueError("email not found in security config: %s" % email)


def set_current_user(email: str) -> None:
    """set current_user in request_context to user
    identified by email.

    Args:
        email (str): email of user account
    """

    if has_request_context():
        u: UserMixin = User.query.filter_by(email=email).first()
        if u is None:
            u = AnonymousUser()
        g._login_user = u

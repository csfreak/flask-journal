import typing as t

from flask import Flask
from flask_security import user_registered

from ..models import Role, User, UserSettings, db


def user_init(app: Flask, user: User, *args: t.Any, **kwargs: t.Any) -> None:
    if user is None:
        return
    if user.settings is None:
        user.settings = UserSettings()
    user_role = Role.find_by_name("user")
    if not user_role:
        raise ValueError("unable to find role: user")
    if user_role not in user.roles:
        user.roles.append(user_role)
    db.session.add(user)
    db.session.commit()


def init_signals(app: Flask) -> None:
    user_registered.connect(user_init, app)

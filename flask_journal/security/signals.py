
from flask import Flask
from flask_security import user_registered

from ..models import Role, User, UserSettings, db


def user_init(app: Flask, user: User, *args, **kwargs) -> None:
    if user is None:
        return
    if user.settings is None:
        user.settings = UserSettings()
    user_role = Role.query.filter_by(name='user').first()
    if user_role not in user.roles:
        user.roles.append(user_role)
    db.session.add(user)
    db.session.commit()


def init_signals(app: Flask):
    user_registered.connect(user_init, app)

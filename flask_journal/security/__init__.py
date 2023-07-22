from flask import Flask
from flask_mailman import Mail
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import config_value as security_config_value
from flask_wtf import CSRFProtect

from ..models import Role, User, db
from . import utils
from .signals import init_signals

security = Security()


def init_security_context_processors() -> None:
    security.login_context_processor(lambda: dict(title='Login'))
    security.forgot_password_context_processor(
        lambda: dict(title='Forgot Password'))
    security.register_context_processor(lambda: dict(title='Register'))
    security.reset_password_context_processor(
        lambda: dict(title='Reset Password'))


def init_security(app: Flask) -> None:
    CSRFProtect(app)
    Mail(app)
    security.init_app(app, SQLAlchemyUserDatastore(db, User, Role))
    init_signals(app)
    init_security_context_processors()
    utils.PASSWORD_LENGTH = security_config_value("PASSWORD_LENGTH_MIN", app=app)

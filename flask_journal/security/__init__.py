from flask import Flask
from flask_security import \
    Security  # pyright: ignore [reportPrivateImportUsage]
from flask_security import \
    SQLAlchemyUserDatastore  # pyright: ignore [reportPrivateImportUsage]
from flask_wtf import CSRFProtect

from ..models import Role, User, db
from .signals import init_signals

security = Security(
)


def init_security(app: Flask) -> None:
    CSRFProtect(app)
    security.init_app(app, SQLAlchemyUserDatastore(db, User, Role))
    init_signals(app)
    security.login_context_processor(lambda: dict(title='Login'))
    security.forgot_password_context_processor(
        lambda: dict(title='Forgot Password'))
    security.register_context_processor(lambda: dict(title='Register'))
    security.reset_password_context_processor(
        lambda: dict(title='Reset Password'))

from flask import Flask
from flask_security import \
    Security  # pyright: ignore [reportPrivateImportUsage]
from flask_security import \
    SQLAlchemyUserDatastore  # pyright: ignore [reportPrivateImportUsage]

from ..models import Role, User, db

security = Security()


def init_security(app: Flask) -> None:
    security.init_app(app, SQLAlchemyUserDatastore(db, User, Role))

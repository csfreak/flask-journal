import logging

from flask import Flask

from .db import db
from .rbac import Role

roles = {
    "admin": {"description": "Administrator: allows user management"},
    "manage": {"description": "Power User: can undelete their own records"},
    "user": {"description": "Basic User: all users have this role"},
}

logger = logging.getLogger(__name__)


def init_roles(app: Flask) -> None:
    with app.app_context():
        for name, role in roles.items():
            if Role.find_by_name(name) is None:
                logger.info(f"Created new role: {name}")
                db.session.add(Role(name=name, **role))
        db.session.commit()


def init_data(app: Flask) -> None:
    with app.app_context():
        db.create_all()  # This should be NOOP
    init_roles(app)

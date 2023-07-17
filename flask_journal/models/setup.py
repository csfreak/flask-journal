
from flask import Flask

from .db import db
from .rbac import Role

roles = {
    'admin': {'description': "Administrator: allows user management"},
    'manage': {'description': "Power User: can undelete their own records"},
    'user': {'description': "Basic User: all users have this role"}
}


def init_roles(app: Flask):
    with app.app_context():
        for name, role in roles.items():
            if Role.query.filter_by(name=name).first() is None:
                app.logger.getChild(__name__).info(f"Created new role: {name}")
                db.session.add(Role(name=name, **role))
        db.session.commit()


def init_data(app: Flask):
    init_roles(app)

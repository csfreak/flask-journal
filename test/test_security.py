import typing as t

from flask import Flask
from flask_security.utils import verify_and_update_password

from flask_journal.models import User as SecurityUser
from flask_journal.security import security

from .base import AppTestBase

# from fakeredis import FakeStrictRedis
# from flask_redis import Redis as FlaskRedis
# from rossItApi.utils.redis import redis

config = {
    "users": [
        {
            "email": "user1@example.test",
            "password": "user1_password",
            "roles": [
                "admin"
                "user"
            ],
            "active": True
        },
        {
            "email": "user2@example.test",
            "password": "user2_password",
            "roles": [
                "user"
            ],
            "active": True
        },
        {
            "email": "user3@example.test",
            "password": "user3_password",
            "roles": [
                "user"
            ],
            "active": False
        }
    ],
    "roles": [
        {
            "name": "admin",
            "description": "admin role"
        },
        {
            "name": "user",
            "description": "user role"
        },
    ],
}


class SecurityUserTest(AppTestBase):
    # def setup(self: t.Self, app: Flask) -> None:
    #     pass

    def tearDown(self: t.Self, app: Flask) -> None:
        app.extensions['sqlalchemy'].session.commit()
        super().tearDown(app)

    def test_app_security_instance(self: t.Self, app: Flask) -> None:
        self.assertEqual(security, app.extensions["security"])

    def test_datastore_create_user(self: t.Self, app: Flask) -> None:
        for user in config['users']:
            enorm = security._mail_util.validate(user['email'])
            pbad, pnorm = security._password_util.validate(
                user['password'], True)

            self.assertIsNone(pbad)

            security.datastore.create_user(
                email=enorm,
                password=pnorm,
                active=user['active']
            )
            u = security.datastore.find_user(
                email=user['email'])
            self.assertTrue(u, SecurityUser)
            self.assertEqual(u.active, user['active'])
            self.assertTrue(verify_and_update_password(
                user['password'], u))  # type: ignore

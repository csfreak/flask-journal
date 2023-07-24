import typing as t
from datetime import datetime

from flask import Flask, url_for
from flask_security.forms import ConfirmRegisterForm
from flask_security.recoverable import generate_reset_password_token
from flask_security.registerable import register_user
from flask_security.utils import verify_and_update_password

from flask_journal.models import Role as SecurityRole
from flask_journal.models import User as SecurityUser
from flask_journal.models import UserSettings
from flask_journal.security import security
from flask_journal.security.signals import user_init

from ..base import AppTestBase
from ..config import html_test_strings, security_config

# from fakeredis import FakeStrictRedis
# from flask_redis import Redis as FlaskRedis
# from rossItApi.utils.redis import redis


class SecurityUserTest(AppTestBase):

    def tearDown(self: t.Self, app: Flask) -> None:
        app.extensions['mailman'].outbox = []
        app.extensions['sqlalchemy'].session.commit()
        super().tearDown(app)

    def test_app_security_instance(self: t.Self, app: Flask) -> None:
        self.assertEqual(security, app.extensions["security"])

    def test_datastore_create_user(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                self.assertIsNone(pbad)

                u: SecurityUser = security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active']
                )
                self.assertTrue(isinstance(u, SecurityUser))
                self.assertEqual(u.active, user['active'])
                self.assertTrue(verify_and_update_password(
                    user['password'], u))

    def test_datastore_register_user(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            # Reset outbox for tests
            app.extensions['mailman'].outbox = []

            with self.subTest(user['email']):
                with app.test_request_context('/auth/register'):
                    register_user(
                        ConfirmRegisterForm(data=dict(email=user['email'], password=user['password']))
                    )
                outbox = app.extensions['mailman'].outbox

                self.assertEqual(len(outbox), 1)
                self.assertIn(user['email'], outbox[0].to)
                u = security.datastore.find_user(
                    email=user['email'])
                self.assertTrue(isinstance(u, SecurityUser))
                self.assertTrue(u.active)
                self.assertIn(security.datastore.find_role('user'), u.roles)

    def test_datastore_create_role(self: t.Self, app: Flask) -> None:
        for role in security_config['roles']:
            with self.subTest(role['name']):
                security.datastore.create_role(**role)
                r = security.datastore.find_role(role['name'])
                self.assertTrue(isinstance(r, SecurityRole))
                self.assertEqual(r.name, role['name'])

    def test_user_has_role(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                u: SecurityUser = security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active']
                )

                for role in user['roles']:
                    security.datastore.add_role_to_user(u, role)

                self.assertListEqual(user['roles'], [r.name for r in u.roles])

                for role in user['roles']:
                    self.assertTrue(u.has_role(role))

    def test_user_missing_role(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                u: SecurityUser = security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active']
                )

                self.assertFalse(u.has_role('testing'))

    def test_user_login(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active'],
                    confirmed_at=datetime.now()
                )

                with app.test_client() as c:
                    c.get('/auth/login')
                    rv = c.post('/auth/login',
                                data={
                                    'email': user['email'],
                                    'password': user['password']
                                })
                    if user['active']:
                        self.assertStatus(rv, 302)
                        self.assertLocationHeader(rv, '/')
                        c.post('/auth/logout')
                    else:
                        self.assertStatus(rv, 200)
                        self.assertIn(html_test_strings['title'] % 'Login', rv.text)
                    c.delete_cookie('session')

    def test_user_login_invalid_password(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active'],
                    confirmed_at=datetime.now()
                )

                with app.test_client() as c:
                    rv = c.post(url_for('security.login'),
                                data={
                        'email': user['email'],
                        'password': 'invalidpassword',
                    })
                    self.assertIn(html_test_strings['security']['error']['generic'], rv.text)
                    self.assertIn(html_test_strings['title'] % 'Login', rv.text)

    def test_user_login_not_confirmed(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active']
                )

                with app.test_client() as c:
                    rv = c.post(url_for('security.login'),
                                data={
                        'email': user['email'],
                        'password': user['password'],
                    })
                    self.assertIn(html_test_strings['security']['error']['email_confirm'], rv.text)
                    self.assertIn(html_test_strings['title'] % 'Login', rv.text)

    def test_user_login_non_existent(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active'],
                    confirmed_at=datetime.now()
                )

                with app.test_client() as c:
                    rv = c.post(url_for('security.login'),
                                data={
                        'email': 'baduser@example.test',
                        'password': user['password'],
                    })
                    self.assertIn(html_test_strings['security']['error']['generic'], rv.text)
                    self.assertIn(html_test_strings['title'] % 'Login', rv.text)

    def test_user_login_invalid_email(self: t.Self, app: Flask) -> None:
        for user in security_config['users']:
            with self.subTest(user['email']):
                enorm = security._mail_util.validate(user['email'])
                pbad, pnorm = security._password_util.validate(
                    user['password'], True)

                security.datastore.create_user(
                    email=enorm,
                    password=pnorm,
                    active=user['active'],
                    confirmed_at=datetime.now()
                )

                with app.test_client() as c:
                    rv = c.post(url_for('security.login'),
                                data={
                        'email': 'notanemailaddress&1',
                        'password': user['password'],
                    })
                    self.assertIn(html_test_strings['security']['error']['generic'], rv.text)
                    self.assertIn(html_test_strings['title'] % 'Login', rv.text)

    def test_context_processors(self: t.Self, app: Flask) -> None:
        for endpoint in ['login', 'register', 'forgot_password']:
            title: str = endpoint.replace('_', ' ').title()
            with self.subTest(endpoint=endpoint):
                with app.test_client() as c:
                    rv = c.get(url_for(f"security.{endpoint}"))
                    self.assertIn(html_test_strings['title'] % title, rv.text)

    def test_context_processor_reset_password(self: t.Self, app: Flask) -> None:
        user = security_config['users'][0]
        enorm = security._mail_util.validate(user['email'])
        pbad, pnorm = security._password_util.validate(
            user['password'], True)

        u: SecurityUser = security.datastore.create_user(
            email=enorm,
            password=pnorm,
            active=user['active'],
            confirmed_at=datetime.now()
        )

        with app.test_client() as c:
            rv = c.get(
                url_for(
                    "security.reset_password",
                    token=generate_reset_password_token(u)))
            self.assertIn(html_test_strings['title'] % 'Reset Password', rv.text)

    def test_user_init_handler(self: t.Self, app: Flask) -> None:
        user = security_config['users'][0]
        enorm = security._mail_util.validate(user['email'])
        pbad, pnorm = security._password_util.validate(
            user['password'], True)

        u: SecurityUser = security.datastore.create_user(
            email=enorm,
            password=pnorm,
            active=user['active'],
            confirmed_at=datetime.now()
        )

        user_init(app, u)

        self.assertIsNotNone(u.settings)
        self.assertTrue(u.has_role('user'))

    def test_user_init_handler_no_user(self: t.Self, app: Flask) -> None:
        user = security_config['users'][0]
        enorm = security._mail_util.validate(user['email'])
        pbad, pnorm = security._password_util.validate(
            user['password'], True)

        u: SecurityUser = security.datastore.create_user(
            email=enorm,
            password=pnorm,
            active=user['active'],
            confirmed_at=datetime.now()
        )

        user_init(app, None)

        self.assertIsNone(u.settings)
        self.assertFalse(u.has_role('user'))

    def test_user_init_handler_existing_settings(self: t.Self, app: Flask) -> None:
        user = security_config['users'][0]
        enorm = security._mail_util.validate(user['email'])
        pbad, pnorm = security._password_util.validate(
            user['password'], True)

        u: SecurityUser = security.datastore.create_user(
            email=enorm,
            password=pnorm,
            active=user['active'],
            confirmed_at=datetime.now()
        )
        us = UserSettings()
        u.settings = us
        user_init(app, u)

        self.assertIs(u.settings, us)
        self.assertTrue(u.has_role('user'))

    def test_user_init_handler_existing_role(self: t.Self, app: Flask) -> None:
        user = security_config['users'][0]
        enorm = security._mail_util.validate(user['email'])
        pbad, pnorm = security._password_util.validate(
            user['password'], True)

        u: SecurityUser = security.datastore.create_user(
            email=enorm,
            password=pnorm,
            active=user['active'],
            confirmed_at=datetime.now()
        )
        security.datastore.add_role_to_user(u, 'user')
        user_init(app, u)

        self.assertIsNotNone(u.settings)
        self.assertTrue(u.has_role('user'))

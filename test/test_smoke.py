import typing as t

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_journal.models import db

from .base import AppTestBase

# from fakeredis import FakeStrictRedis
# from flask_redis import Redis as FlaskRedis
# from rossItApi.utils.redis import redis


class SmokeTest(AppTestBase):
    def test_smoke_app(self: t.Self, app: Flask) -> None:
        self.assertTrue(isinstance(app, Flask))

    def test_smoke_app_config(self: t.Self, app: Flask) -> None:
        self.assertTrue(app.config["TESTING"])

    def test_smoke_db(self: t.Self, app: Flask) -> None:
        self.assertTrue(isinstance(db, SQLAlchemy))
        self.assertEqual(db, app.extensions["sqlalchemy"])

    # def test_smoke_redis(self: t.Self, app: Flask) -> None:
    #     self.assertTrue(isinstance(redis, FlaskRedis))
    #     self.assertTrue(isinstance(redis.connection, FakeStrictRedis))
    #     self.assertEqual(redis.connection, app.extensions["redis"]['REDIS'])

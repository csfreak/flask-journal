import logging
import os
import typing as t
from datetime import timedelta

from flask import Flask


class DefaultConfig(object):
    # FLASK CORE
    SECRET_KEY = "ChangeMe"  # ChangeMe

    # SQLALCHEMY
    # "SQLALCHEMY_DATABASE_URI": "sqlite://", ChangeMe

    # MAIL
    MAIL_DEFAULT_SENDER = "journal@localhost"  # ChangeMe
    MAIL_SERVER = "localhost"  # ChangeMe
    MAIL_PORT = 25  # ChangeMe
    # "MAIL_USERNAME"
    # "MAIL_PASSWORD"
    # SECURITY
    SECURITY_URL_PREFIX = "/auth"
    SECURITY_FLASH_MESSAGES = True
    SECURITY_PASSWORD_HASH = "argon2"
    SECURITY_PASSWORD_SALT = None  # ChangeMe
    SECURITY_HASHING_SCHEMES = ["sha256_crypt"]
    SECURITY_DEPRECATED_HASHING_SCHEMES = []
    SECURITY_PASSWORD_LENGTH_MIN = 8
    SECURITY_PASSWORD_REQUIRED = True
    SECURITY_TOKEN_MAX_AGE = 2592000
    SECURITY_RETURN_GENERIC_RESPONSES = True
    SECURITY_FRESHNESS = timedelta(hours=24)

    # FLASK_SECURITY_LOGIN_URL
    # FLASK_SECURITY_LOGOUT_URL
    # FLASK_SECURITY_LOGOUT_METHODS
    # FLASK_SECURITY_POST_LOGIN_VIEW
    # FLASK_SECURITY_POST_LOGOUT_VIEW
    # FLASK_SECURITY_UNAUTHORIZED_VIEW
    # FLASK_SECURITY_LOGIN_USER_TEMPLATE
    # FLASK_SECURITY_VERIFY_URL
    # FLASK_SECURITY_VERIFY_TEMPLATE
    # FLASK_SECURITY_POST_VERIFY_URL

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_EMAIL_SUBJECT_REGISTER = "Welcome to your journal"
    # FLASK_SECURITY_REGISTER_USER_TEMPLATE
    # FLASK_SECURITY_POST_REGISTER_VIEW
    # FLASK_SECURITY_REGISTER_URL

    SECURITY_CONFIRMABLE = "True"
    # FLASK_SECURITY_CONFIRM_EMAIL_WITHIN
    # FLASK_SECURITY_CONFIRM_URL
    # FLASK_SECURITY_SEND_CONFIRMATION_TEMPLATE
    # FLASK_SECURITY_EMAIL_SUBJECT_CONFIRM
    # FLASK_SECURITY_CONFIRM_ERROR_VIEW
    # FLASK_SECURITY_POST_CONFIRM_VIEW
    # FLASK_SECURITY_AUTO_LOGIN_AFTER_CONFIRM
    # FLASK_SECURITY_LOGIN_WITHOUT_CONFIRMATION
    # FLASK_SECURITY_REQUIRES_CONFIRMATION_ERROR_VIEW

    SECURITY_CHANGEABLE = "True"
    # FLASK_SECURITY_CHANGE_URL
    # FLASK_SECURITY_POST_CHANGE_VIEW
    # FLASK_SECURITY_CHANGE_PASSWORD_TEMPLATE
    # FLASK_SECURITY_SEND_PASSWORD_CHANGE_EMAIL
    # FLASK_SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE

    SECURITY_RECOVERABLE = "True"
    # FLASK_SECURITY_RESET_URL
    # FLASK_SECURITY_RESET_PASSWORD_TEMPLATE
    # FLASK_SECURITY_FORGOT_PASSWORD_TEMPLATE
    # FLASK_SECURITY_POST_RESET_VIEW
    # FLASK_SECURITY_RESET_VIEW
    # FLASK_SECURITY_RESET_ERROR_VIEW
    # FLASK_SECURITY_RESET_PASSWORD_WITHIN
    # FLASK_SECURITY_SEND_PASSWORD_RESET_EMAIL
    # FLASK_SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL
    # FLASK_SECURITY_EMAIL_SUBJECT_PASSWORD_RESET
    # FLASK_SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE

    SECURITY_TRACKABLE = "True"


class Config(DefaultConfig):

    def __init__(self: t.Self,
                 mapping: t.Mapping[str, t.Any] | None = None,
                 **kwargs: t.Any) -> None:
        super().__init__()
        self.IS_GUNICORN = bool(os.getenv('IS_GUNICORN', False))
        if mapping:
            self._load_mapping(mapping)
        self._load_mapping(kwargs)

    def _load_mapping(self: t.Self, mapping: t.Mapping[str, t.Any]) -> None:
        for key, value in mapping.items():
            setattr(self, key, value)


def init_config(app: Flask, c: Config | None) -> None:
    if c is None:
        c = Config()
    app.config.from_object(c)

    set_debug_opts(app)
    set_env_opts(app)

    for k, v in app.config.items():
        app.logger.debug("Setting %s has %s", k, v)


def set_debug_opts(app: Flask) -> None:
    if not app.debug:
        return
    app.config['EXPLAIN_TEMPLATE_LOADING'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    logging.getLogger().setLevel(logging.DEBUG)


def set_env_opts(app: Flask) -> None:
    if not app.testing:
        app.config.from_prefixed_env("JOURNAL")

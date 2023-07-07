import os
import typing as t

from flask.config import Config as FlaskConfig


def load_config() -> FlaskConfig:
    return load_env()


def new_config() -> FlaskConfig:
    c: FlaskConfig = FlaskConfig('')
    c['IS_GUNICORN'] = bool(os.getenv('IS_GUNICORN', False))
    return c


def load_env(prefix: str | None = None) -> FlaskConfig:
    c: FlaskConfig = new_config()

    if not prefix:
        prefix = "FLASK"

    c.from_prefixed_env(prefix=prefix)

    return c


def load_mapping(mapping: t.Mapping[str, t.Any]) -> FlaskConfig:
    c: FlaskConfig = new_config()

    c.from_mapping(mapping)

    return c

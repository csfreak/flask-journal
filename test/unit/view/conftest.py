import logging
import typing as t

import pytest
from flask import Flask

from flask_journal import views

from . import MockDB, MockForm, MockModel, MockSelect

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def route(app: Flask) -> str:
    route = "/tests"

    logger.debug("Add route %s to App", route)

    @app.route(route)
    def test() -> None:
        pass

    return route


@pytest.fixture
def form_class() -> MockForm:
    class form(MockForm):
        def __new__(cls: t.Self, *args: t.Any, **kwargs: t.Any) -> t.Self:
            if not hasattr(cls, "instance"):
                cls.instance = super().__new__(cls, *args, **kwargs)
            return cls.instance

    logger.debug("Create new MockForm class")
    return form


@pytest.fixture
def mock_db(monkeypatch: pytest.MonkeyPatch) -> None:
    db = MockDB()
    monkeypatch.setattr(views.base, "db", db)
    monkeypatch.setattr(views.tag, "db", db)


@pytest.fixture
def model_class(monkeypatch: pytest.MonkeyPatch, mock_db: None) -> MockModel:
    class model(MockModel):
        user = None
        _select = None

        @classmethod
        @property
        def select(cls: t.Self) -> MockSelect:
            if cls._select is None:
                cls._select = MockSelect(cls)
            return cls._select

    monkeypatch.setattr(views.utils, "select", model.select)
    logger.debug("Create new MockModel class")
    return model

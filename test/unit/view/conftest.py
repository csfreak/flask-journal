import logging
import typing as t

import pytest
from flask import Flask

from . import MockForm, MockModel, MockQuery

logger = logging.getLogger(__name__)


@pytest.fixture
def model_class() -> MockModel:
    class model(MockModel):
        query = MockQuery()
        user = None

    logger.debug("Create new MockModel class")
    return model


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

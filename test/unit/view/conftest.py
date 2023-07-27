import typing as t

import pytest
from flask import Flask

from . import MockForm, MockModel, MockQuery


@pytest.fixture
def model_class() -> MockModel:
    class model(MockModel):
        query = MockQuery()

    return model


@pytest.fixture
def route(app: Flask) -> str:
    route = "/tests"

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

    return form

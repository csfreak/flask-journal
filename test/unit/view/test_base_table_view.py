import logging
import typing as t
from datetime import datetime

import pytest
from flask import Flask

from flask_journal.views import base as base_view

from ...config import html_test_strings
from . import MockModel, Model

logger = logging.getLogger(__name__)


@pytest.fixture
def table_results(
    request: pytest.FixtureRequest, model_class: MockModel
) -> list[Model]:
    results: list[Model] = []
    for i in range(request.param):
        m = model_class()
        m.id = i + 1
        m.created_at = datetime.now()
        m.deleted_at = None
        results.append(m)
    return results


@pytest.mark.parametrize(
    "test_string",
    [
        html_test_strings["title"] % "Test",
        html_test_strings["table"]["base"],
        html_test_strings["table"]["pager"]["form"],
        html_test_strings["table"]["create"] % "/tests",
    ],
    ids=["title", "table_base", "table_pager", "table_create"],
)
@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_no_results(
    app: Flask, route: str, model_class: MockModel, test_string: str
) -> None:
    model_class.select._items = []  # LegacyQuery

    with app.test_request_context(route):
        rv = base_view.table_view(model_class, endpoint="test")

        assert test_string in rv


@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.parametrize("table_results", [1, 9], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_1_page_result(
    app: Flask,
    route: str,
    model_class: MockModel,
    table_results: list[Model],
) -> None:
    model_class.select._items = table_results  # LegacyQuery
    test_titles = [("id", "ID", 2), ("created_at", "Created At", 4)]

    with app.test_request_context(route):
        rv = base_view.table_view(model_class, endpoint="test", titles=test_titles)
        logger.debug(rv)
        for _, name, size in test_titles:
            assert html_test_strings["table"]["title"] % (size, name) in rv
        for item in table_results:
            assert html_test_strings["table"]["row_link"] % item.id in rv, (
                "missing row %d link" % item.id
            )
            assert (
                html_test_strings["table"]["row_data"] % (item.id, str(item.created_at))
                in rv
            ), ("missing row %d data" % item.id)


@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.parametrize("table_results", [11, 20], indirect=True)
@pytest.mark.parametrize("page_number", [1, 2])
@pytest.mark.usefixtures("logged_in_user_context")
def test_2_page_result(
    app: Flask,
    route: str,
    model_class: MockModel,
    table_results: list[Model],
    page_number: int,
) -> None:
    model_class.select._items = table_results  # LegacyQuery
    test_titles = [("id", "ID", 2), ("created_at", "Created At", 4)]

    with app.test_request_context(f"{route}?page={page_number}"):
        rv = base_view.table_view(model_class, endpoint="test", titles=test_titles)
        logger.debug(rv)
        for _, name, size in test_titles:
            assert html_test_strings["table"]["title"] % (size, name) in rv
        for item in table_results:
            if item.id > (page_number - 1) * 10 and item.id <= page_number * 10:
                assert html_test_strings["table"]["row_link"] % item.id in rv, (
                    "missing row %d link" % item.id
                )
                assert (
                    html_test_strings["table"]["row_data"]
                    % (item.id, str(item.created_at))
                    in rv
                ), ("missing row %d data" % item.id)
            else:
                assert (
                    html_test_strings["table"]["row_data"]
                    % (item.id, str(item.created_at))
                    not in rv
                ), ("extra row %d data" % item.id)


@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.parametrize("order_field", [None, "id", "created_at", "invalid"])
@pytest.mark.usefixtures("logged_in_user_context")
def test_order_field(
    app: Flask,
    route: str,
    model_class: MockModel,
    order_field: str | None,
) -> None:
    model_class.select._items = []  # LegacyQuery

    with app.test_request_context(route):
        base_view.table_view(model_class, endpoint="test", order_field=order_field)
        if order_field == "invalid" or order_field is None:
            assert not model_class.select.order_field  # LegacyQuery
        else:
            assert model_class.select.order_field  # LegacyQuery


@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.parametrize("order_field", [None, "id", "created_at", "invalid"])
@pytest.mark.usefixtures("logged_in_user_context")
def test_order_field_descending(
    app: Flask,
    route: str,
    model_class: MockModel,
    order_field: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model_class.select._items = []  # LegacyQuery

    def desc(*args: t.Any) -> str:
        return str(args)

    monkeypatch.setattr(base_view, "desc", value=desc)

    with app.test_request_context(route):
        base_view.table_view(
            model_class, endpoint="test", order_field=order_field, descending=True
        )
        if order_field == "invalid" or order_field is None:
            assert not model_class.select.order_field  # LegacyQuery
            assert not model_class.select.order_desc  # LegacyQuery
        else:
            assert model_class.select.order_field  # LegacyQuery
            assert model_class.select.order_desc  # LegacyQuery

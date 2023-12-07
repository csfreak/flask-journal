import logging
import typing as t
from datetime import datetime

import pytest
from werkzeug.exceptions import HTTPException

from flask_journal.views import base as base_view

from . import Form, MockFlash, Model

logger = logging.getLogger(__name__)


@pytest.fixture
def obj_id(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> int | None:
    def get_id() -> int | None:
        return request.param

    logger.debug("patching request_id as %s", request.param)
    monkeypatch.setattr(base_view.utils, "process_request_id", get_id)
    return request.param


@pytest.fixture(autouse=True)
def render_form(monkeypatch: pytest.MonkeyPatch) -> None:
    def mock_render_form(**kwargs: t.Any) -> dict[str, t.Any]:
        return kwargs

    logging.debug("patching render_form")
    monkeypatch.setattr(base_view, "render_form", mock_render_form)


@pytest.fixture
def form_action(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> str:
    def mock_submit_action(form: Form) -> str:
        form.action = request.param
        return request.param

    logging.debug("patching form_submit_action to %s", request.param)
    monkeypatch.setattr(base_view.utils, "form_submit_action", mock_submit_action)
    return request.param


@pytest.fixture
def flash(
    monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest
) -> dict[str : t.Any]:
    logger.debug("patching flash")
    flash = MockFlash(**request.param)
    monkeypatch.setattr(base_view, "flash", flash.flash)
    yield flash


@pytest.fixture
def error(request: pytest.FixtureRequest) -> Exception | None:
    return request.param


@pytest.mark.parametrize("obj_id", [None, 1], indirect=True)
@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_get(model_class: Model, obj_id: None, form_class: Form) -> None:
    model = None
    expected_rf = {"form": form_class(), "model": model_class, "action": "new"}
    if obj_id:
        model = model_class()
        model.id = obj_id
        model_class.select._items = [model]  # LegacyQuery
        expected_rf.pop("action")

    rf = base_view.form_view(model_class, form_class, "")
    assert rf == expected_rf
    assert form_class().obj is model


@pytest.mark.parametrize("obj_id", [1], indirect=True)
@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_get_fail(model_class: Model, obj_id: None, form_class: Form) -> None:
    expected_rf = {"form": form_class(), "model": model_class, "action": "new"}
    if obj_id:
        expected_rf.pop("action")
    with pytest.raises(HTTPException):
        base_view.form_view(model_class, form_class, "")


@pytest.mark.parametrize(
    ("user", "obj_id", "form_action", "flash", "error"),
    [
        (
            "user3@example.test",
            None,
            "Create",
            {"message": "model Created", "category": "message"},
            None,
        ),
        (
            "user3@example.test",
            1,
            "Create",
            {},
            HTTPException,
        ),
        (
            "user3@example.test",
            404,
            "Update",
            {},
            HTTPException,
        ),
        (
            "user3@example.test",
            1,
            "Update",
            {"message": "model Updated", "category": "message"},
            None,
        ),
        (
            "user3@example.test",
            404,
            "Edit",
            {},
            HTTPException,
        ),
        (
            "user3@example.test",
            1,
            "Edit",
            {},
            None,
        ),
        (
            "user3@example.test",
            404,
            "Undelete",
            {},
            HTTPException,
        ),
        (
            "user3@example.test",
            1,
            "Undelete",
            {"message": "Unable to Undelete model", "category": "error"},
            None,
        ),
        (
            "user2@example.test",
            1,
            "Undelete",
            {"message": "model Restored", "category": "warning"},
            None,
        ),
        (
            "user3@example.test",
            404,
            "Delete",
            {},
            HTTPException,
        ),
        (
            "user3@example.test",
            1,
            "Delete",
            {"message": "model Deleted"},
            None,
        ),
    ],
    ids=[
        "create_success",
        "create_existing",
        "update_missing",
        "update_success",
        "edit_missing",
        "edit_success",
        "undelete_missing",
        "undelete_without_manage_role",
        "undelete_success",
        "delete_missing",
        "delete_success",
    ],
    indirect=True,
)
@pytest.mark.usefixtures("logged_in_user_context", "mock_db")
def test_post(
    obj_id: int | None,
    flash: MockFlash,
    route: str,
    model_class: Model,
    form_class: Form,
    form_action: str,
    error: Exception | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = None
    expected_rf = {
        "form": form_class(),
        "model": model_class,
        "action": "new",
    }
    form_class()._valid = True
    if obj_id and not error and form_action != "Create":
        model = model_class()
        model.id = obj_id
        model_class.select._items = [model]  # LegacyQuery
        expected_rf.pop("action")
        match form_action:
            case "Undelete":
                model.deleted_at = datetime.now()
            case "Edit":
                expected_rf["action"] = "edit"
            case "Delete":
                expected_rf = route

                def redirect(url: str) -> str:
                    return url

                monkeypatch.setattr(base_view, "redirect", redirect)

    if error:
        with pytest.raises(error):
            base_view.form_view(model_class, form_class, route)
    else:
        rf = base_view.form_view(model_class, form_class, "test")
        assert rf == expected_rf

        match form_action:
            case "Create":
                assert form_class().obj == form_class().populated
            case "Update":
                assert form_class().obj is model
                assert form_class().obj == form_class().populated
            case "Delete":
                assert form_class().obj is model
                assert isinstance(model.deleted_at, datetime)
            case "Undelete" if flash.expected["category"] != "error":
                assert model.deleted_at is None
            case _:
                assert form_class().obj is model
        assert flash.called == flash.expected

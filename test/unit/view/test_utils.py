import pytest
import wtforms
from flask import Flask
from werkzeug.exceptions import HTTPException

from flask_journal.forms.base import CustomForm
from flask_journal.models import User
from flask_journal.views import utils as view_utils

from . import MockModel


def test_process_request_id_none(app: Flask) -> None:
    with app.test_request_context():
        r_id: int | None = view_utils.process_request_id()
        assert r_id is None


def test_process_request_id_arg(app: Flask) -> None:
    with app.test_request_context(query_string={"id": "1"}):
        r_id: int | None = view_utils.process_request_id()
        assert r_id == 1


def test_process_request_id_form(app: Flask) -> None:
    with app.test_request_context(method="POST", data={"id": "1"}):
        r_id: int | None = view_utils.process_request_id()
        assert r_id == 1


def test_process_request_id_both(app: Flask) -> None:
    with app.test_request_context(
        method="POST", data={"id": "1"}, query_string={"id": "2"}
    ):
        r_id: int | None = view_utils.process_request_id()
        assert r_id == 1


def test_form_submit_action_no_submit(app: Flask) -> None:
    with app.test_request_context(method="GET", data={"id": "1"}):
        with pytest.raises(ValueError):
            view_utils.form_submit_action(CustomForm())


def test_form_submit_action_submit_no_button(app: Flask) -> None:
    with app.test_request_context(method="POST", data={"id": "1"}):
        with pytest.raises(ValueError):
            view_utils.form_submit_action(CustomForm())


@pytest.mark.parametrize(
    "action", ["Create", "Edit", "Update", "Delete", "Undelete", "Custom"]
)
def test_form_submit_action(app: Flask, action: str) -> None:
    class TestForm(CustomForm):
        custom = wtforms.fields.BooleanField(
            name="Custom", widget=wtforms.widgets.SubmitInput
        )

    with app.test_request_context(method="POST", data={"id": "1", action: action}):
        r_action: str = view_utils.form_submit_action(TestForm())
        assert r_action == action


@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_build_select_user_no_filters(
    app: Flask, user: User, model_class: MockModel
) -> None:
    r_select = view_utils.build_select(model_class)

    assert r_select.filter == dict(user=user)
    assert not r_select.include_deleted


@pytest.mark.parametrize("user", ["user2@example.test"], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_build_select_user_manage(app: Flask, model_class: MockModel) -> None:
    r_select = view_utils.build_select(model_class)

    assert r_select.include_deleted


@pytest.mark.parametrize("user", ["user3@example.test"], indirect=True)
@pytest.mark.usefixtures("logged_in_user_context")
def test_build_select_user_filters(
    app: Flask, user: User, monkeypatch: pytest.MonkeyPatch, model_class: MockModel
) -> None:
    r_select = view_utils.build_select(model_class, filters={"id": 1})

    assert r_select.filter == dict(user=user, id=1)
    assert not r_select.include_deleted


@pytest.mark.parametrize(
    "user",
    ["user3@example.test", "user1@example.test"],
    indirect=True,
)
@pytest.mark.usefixtures("logged_in_user_context")
def test_build_select_user_no_user_model(
    app: Flask, user: User, monkeypatch: pytest.MonkeyPatch, model_class: MockModel
) -> None:
    monkeypatch.setattr(model_class, "ownable", False)
    if not user.has_role("admin"):
        with pytest.raises(HTTPException):
            view_utils.build_select(model_class)
    else:
        r_select = view_utils.build_select(model_class)
        assert r_select.filter == dict()

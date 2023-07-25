import typing as t
from copy import deepcopy
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient

from flask_journal.models.base import JournalBaseModel
from flask_journal.views import base as base_view

from ..config import html_test_strings, view_form_action_buttons


@pytest.mark.parametrize(
    "action",
    [
        "invalid",
        "view",
        "new",
        "edit",
        None,
    ],
)
@pytest.mark.parametrize(
    "context", [{"primary_fields": ["id"]}, {"context_var": "string"}, {}]
)
def test_actions(
    app: Flask,
    monkeypatch: pytest.MonkeyPatch,
    action: str,
    context: dict[str, t.Any],
) -> None:
    def mock_render_template(
        *args: t.Any, **kwargs: t.Any
    ) -> tuple[tuple[t.Any], dict[str, t.Any]]:
        return args, kwargs

    monkeypatch.setattr(base_view, "render_template", value=mock_render_template)

    expected_kwargs = deepcopy(context)
    passed_kwargs = deepcopy(context)

    if action:
        expected_kwargs["action"] = action if action else "view"
        passed_kwargs["action"] = action
    else:
        expected_kwargs["action"] = "view"

    passed_kwargs["model"] = JournalBaseModel
    expected_kwargs["form"] = passed_kwargs["form"] = base_view.CustomForm()
    expected_kwargs["title"] = f"{expected_kwargs['action']} JournalBaseModel"
    expected_kwargs.setdefault("primary_fields", None)

    expected_args = ("journal/formbase.html",)

    if action == "invalid":
        with pytest.raises(ValueError):
            base_view.render_form(**passed_kwargs)
    else:
        called: tuple[tuple[t.Any], dict[str, t.Any]] = base_view.render_form(
            **passed_kwargs
        )

        assert called == (expected_args, expected_kwargs)


@pytest.mark.parametrize(
    "logged_in_user_context", ["user3@example.test"], indirect=True
)
@pytest.mark.parametrize("action", ["view", "new", "edit"])
def test_actions_render(logged_in_user_context: FlaskClient, action: str) -> None:
    r: str = base_view.render_form(
        form=base_view.CustomForm(), model=JournalBaseModel, action=action
    )
    assert html_test_strings["title"] % f"{action.title()} Journalbasemodel" in r
    assert 'id="FormPrimaryColumn' not in r
    assert 'id="FormSecondaryColumn' not in r


@pytest.mark.parametrize(
    "logged_in_user_context", ["user3@example.test"], indirect=True
)
@pytest.mark.parametrize("action", ["view", "new", "edit"])
@pytest.mark.parametrize("button", view_form_action_buttons["all"])
def test_actions_render_button(
    logged_in_user_context: FlaskClient, action: str, button: str
) -> None:
    r: str = base_view.render_form(
        form=base_view.CustomForm(), model=JournalBaseModel, action=action
    )
    if button in view_form_action_buttons[action]:
        assert html_test_strings["button"][button] in r
    else:
        assert html_test_strings["button"][button] not in r


@pytest.mark.parametrize(
    "logged_in_user_context", ["user3@example.test"], indirect=True
)
@pytest.mark.parametrize("action", ["view", "new", "edit"])
def test_actions_render_columns(
    logged_in_user_context: FlaskClient, action: str
) -> None:
    r: str = base_view.render_form(
        form=base_view.CustomForm(),
        model=JournalBaseModel,
        action=action,
        primary_fields=["id"],
    )
    assert 'id="FormPrimaryColumn' in r
    assert 'id="FormSecondaryColumn' in r


@pytest.mark.parametrize(
    "logged_in_user_context", ["user3@example.test"], indirect=True
)
@pytest.mark.parametrize("button", view_form_action_buttons["all"])
def test_actions_render_deleted_button(
    logged_in_user_context: FlaskClient, button: str
) -> None:
    r: str = base_view.render_form(
        form=base_view.CustomForm(data={"deleted_at": datetime.now()}),
        model=JournalBaseModel,
    )
    if button == "undelete":
        assert html_test_strings["button"][button] in r
    else:
        assert html_test_strings["button"][button] not in r

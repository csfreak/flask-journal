import logging
import typing as t
from unittest import TestCase

import pytest
from mock import MagicMock, patch
from werkzeug.exceptions import HTTPException

from flask_journal.views import base as base_view

from . import Form, Model

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
def flash(monkeypatch: pytest.MonkeyPatch) -> dict[str : t.Any]:
    response: dict[str, t.Any] = {}

    def mock_flash(message: str, **kwargs: t.Any) -> None:
        response.update(kwargs)
        response.update(message=message)

    logger.debug("patching flash")
    monkeypatch.setattr(base_view, "flash", mock_flash)
    yield response


@pytest.mark.parametrize("obj_id", [None, 1], indirect=True)
@pytest.mark.parametrize(
    "logged_in_user_context", ["user3@example.test"], indirect=True
)
@pytest.mark.usefixtures("logged_in_user_context")
def test_get(
    model_class: Model, obj_id: None, form_class: Form, flash: dict[str, t.Any]
) -> None:
    model = None
    expected_rf = {"form": form_class(), "model": model_class, "action": "new"}
    if obj_id:
        model = model_class()
        model.id = obj_id
        model_class.query._items = [model]
        expected_rf.pop("action")

    rf = base_view.form_view(model_class, form_class, "")
    assert rf == expected_rf
    assert form_class().obj is model


@pytest.mark.parametrize("obj_id", [1], indirect=True)
@pytest.mark.parametrize(
    "logged_in_user_context", ["user3@example.test"], indirect=True
)
@pytest.mark.usefixtures("logged_in_user_context")
def test_get_fail(
    model_class: Model, obj_id: None, form_class: Form, flash: dict[str, t.Any]
) -> None:
    expected_rf = {"form": form_class(), "model": model_class, "action": "new"}
    if obj_id:
        expected_rf.pop("action")
    with pytest.raises(HTTPException):
        base_view.form_view(model_class, form_class, "")


class FormViewFunctionTest(TestCase):
    def setUp(self: t.Self) -> None:
        self.mock_render_form: MagicMock = patch(
            "flask_journal.views.base.render_form"
        ).start()
        self.mock_utils: MagicMock = patch("flask_journal.views.base.utils").start()
        self.mock_redirect: MagicMock = patch(
            "flask_journal.views.base.redirect"
        ).start()
        self.mock_db: MagicMock = patch("flask_journal.views.base.db").start()
        self.mock_flash: MagicMock = patch("flask_journal.views.base.flash").start()
        self.mock_abort: MagicMock = patch("flask_journal.views.base.abort").start()
        self.mock_current_user: MagicMock = patch(
            "flask_journal.views.base.current_user", new_callable=MagicMock
        ).start()
        self.mock_url_for: MagicMock = patch("flask_journal.views.base.url_for").start()

        self.mock_abort.side_effect = HTTPException()

        self.form_class = MagicMock(name="CustomForm")
        self.model_class = MagicMock(name="JournalBaseModel")
        self.model_class.configure_mock(__name__="JournalBaseModelMock")
        return super().setUp()

    def tearDown(self: t.Self) -> None:
        patch.stopall()
        return super().tearDown()

    def test_id_none_create(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Create"
        base_view.form_view(self.model_class, self.form_class, "")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": None}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.model_class.assert_called_once_with(user=self.mock_current_user)
        self.form_class.return_value.populate_obj.assert_called_once_with(
            self.model_class.return_value
        )
        self.mock_db.session.add.assert_called_once_with(self.model_class.return_value)
        self.mock_db.session.commit.assert_called_once_with()
        self.mock_flash.assert_called_once_with(
            "JournalBaseModelMock Created", category="message"
        )
        self.mock_render_form.assert_called_once_with(
            form=self.form_class.return_value, model=self.model_class
        )
        self.mock_redirect.assert_not_called()
        self.mock_abort.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_id_set_create(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Create"
        try:
            base_view.form_view(self.model_class, self.form_class, "")
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail("abort not called")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_render_form.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_exists_update(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Update"
        base_view.form_view(self.model_class, self.form_class, "")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.form_class.return_value.process.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.populate_obj.assert_called_once_with(
            self.mock_utils.build_query.return_value.first.return_value
        )
        self.mock_db.session.add.assert_called_once_with(
            self.mock_utils.build_query.return_value.first.return_value
        )
        self.mock_db.session.commit.assert_called_once_with()
        self.mock_flash.assert_called_once_with(
            "JournalBaseModelMock Updated", category="message"
        )
        self.mock_render_form.assert_called_once_with(
            form=self.form_class.return_value, model=self.model_class
        )
        self.mock_redirect.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_none_update(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Update"
        try:
            base_view.form_view(self.model_class, self.form_class, "")
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail("abort not called")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_render_form.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_set_edit(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Edit"
        base_view.form_view(self.model_class, self.form_class, "")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_render_form.assert_called_once_with(
            action="edit", form=self.form_class.return_value, model=self.model_class
        )
        self.mock_redirect.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_none_edit(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Edit"
        try:
            base_view.form_view(self.model_class, self.form_class, "")
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail("abort not called")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_render_form.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_set_delete(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Delete"
        base_view.form_view(self.model_class, self.form_class, "test_endpoint")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_utils.build_query.return_value.first.return_value.delete.assert_called_once_with()
        self.mock_db.session.add.assert_called_once_with(
            self.mock_utils.build_query.return_value.first.return_value
        )
        self.mock_db.session.commit.assert_called_once_with()
        self.mock_flash.assert_called_once_with("JournalBaseModelMock Deleted")
        self.mock_url_for.assert_called_once_with("test_endpoint")
        self.mock_redirect.assert_called_once_with(self.mock_url_for.return_value)
        self.mock_render_form.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.form_class.return_value.process.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()

    def test_obj_none_delete(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Delete"
        try:
            base_view.form_view(self.model_class, self.form_class, "")
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail("abort not called")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_render_form.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called

    def test_obj_set_undelete(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Undelete"
        self.mock_current_user.has_role.return_value = True
        base_view.form_view(self.model_class, self.form_class, "test_endpoint")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_current_user.has_role.assert_called_once_with("manage")
        self.mock_utils.build_query.return_value.first.return_value.undelete.assert_called_once_with()
        self.mock_db.session.add.assert_called_once_with(
            self.mock_utils.build_query.return_value.first.return_value
        )
        self.mock_db.session.commit.assert_called_once_with()
        self.form_class.return_value.process.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.mock_flash.assert_called_once_with(
            "JournalBaseModelMock Restored", category="warning"
        )
        self.mock_render_form.assert_called_once_with(
            form=self.form_class.return_value, model=self.model_class
        )
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_none_undelete(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Undelete"
        try:
            base_view.form_view(self.model_class, self.form_class, "")
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail("abort not called")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_current_user.has_role.assert_not_called()
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.form_class.return_value.process.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_render_form.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called

    def test_obj_set_undelete_no_role(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = "Undelete"
        self.mock_current_user.has_role.return_value = False
        base_view.form_view(self.model_class, self.form_class, "")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={"id": 1}
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value
        )
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_current_user.has_role.assert_called_once_with("manage")
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.form_class.return_value.process.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_abort.assert_not_called()
        self.mock_flash.assert_called_once_with(
            "Unable to Undelete JournalBaseModelMock", category="error"
        )
        self.mock_render_form.assert_called_once_with(
            form=self.form_class.return_value, model=self.model_class
        )
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called()

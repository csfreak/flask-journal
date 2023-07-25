import typing as t
from datetime import datetime
from unittest import TestCase

import wtforms
from flask import Flask
from flask_security import current_user
from mock import MagicMock, patch
from werkzeug.exceptions import HTTPException

from flask_journal.forms.base import CustomForm
from flask_journal.models.base import JournalBaseModel
from flask_journal.views import base as base_view
from flask_journal.views import utils as view_utils

from ..base import UserAppTestBase
from ..config import html_test_strings
from ..utils import set_current_user


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

    def test_id_none_get(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = False
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
        self.mock_render_form.assert_called_once_with(
            action="new", form=self.form_class.return_value, model=self.model_class
        )
        self.mock_redirect.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_id_set_get(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.form_class.return_value.validate_on_submit.return_value = False
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
            form=self.form_class.return_value, model=self.model_class
        )
        self.mock_redirect.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_id_set_object_none_get(self: t.Self) -> None:
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = False
        try:
            base_view.form_view(self.model_class, self.form_class, "")
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail("abort not called")
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class,
            filters={"id": self.mock_utils.process_request_id.return_value},
        )
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=None)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_render_form.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_flash.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

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


class ViewUtilsFunctionTest(UserAppTestBase):
    def test_process_request_id_none(self: t.Self, app: Flask) -> None:
        with app.test_request_context():
            set_current_user("user1@example.test")
            r_id: int | None = view_utils.process_request_id()
            self.assertIsNone(r_id)

    def test_process_request_id_arg(self: t.Self, app: Flask) -> None:
        with app.test_request_context(query_string={"id": "1"}):
            set_current_user("user1@example.test")
            r_id: int | None = view_utils.process_request_id()
            self.assertIsInstance(r_id, int)
            self.assertEqual(r_id, 1)

    def test_process_request_id_form(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method="POST", data={"id": "1"}):
            set_current_user("user1@example.test")
            r_id: int | None = view_utils.process_request_id()
            self.assertIsInstance(r_id, int)
            self.assertEqual(r_id, 1)

    def test_process_request_id_both(self: t.Self, app: Flask) -> None:
        with app.test_request_context(
            method="POST", data={"id": "1"}, query_string={"id": "2"}
        ):
            r_id: int | None = view_utils.process_request_id()
            self.assertIsInstance(r_id, int)
            self.assertEqual(r_id, 1)

    def test_form_submit_action_no_submit(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method="GET", data={"id": "1"}):
            form = CustomForm()
            self.assertRaises(ValueError, view_utils.form_submit_action, form)

    def test_form_submit_action_submit_no_button(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method="POST", data={"id": "1"}):
            form = CustomForm()
            self.assertRaises(ValueError, view_utils.form_submit_action, form)

    def test_form_submit_action(self: t.Self, app: Flask) -> None:
        class TestForm(CustomForm):
            custom = wtforms.fields.BooleanField(
                name="Custom", widget=wtforms.widgets.SubmitInput
            )

        for action in ["Create", "Edit", "Update", "Delete", "Undelete", "Custom"]:
            with self.subTest(action=action):
                expected: str = action
                with app.test_request_context(
                    method="POST", data={"id": "1", expected: expected}
                ):
                    form = TestForm()
                    r_action: str = view_utils.form_submit_action(form)
                    self.assertEqual(r_action, expected)

    def test_build_query_user_no_filters(self: t.Self, app: Flask) -> None:
        model_class = MagicMock(name="JournalBaseModelMock")
        with app.test_request_context():
            set_current_user("user3@example.test")
            r_query = view_utils.build_query(model_class)
            self.assertIsInstance(r_query, MagicMock)
            model_class.query.filter_by.assert_called_once_with(user=current_user)
            model_class.query.filter_by.return_value.execution_options.assert_called_once_with(
                include_deleted=False
            )

    def test_build_query_user_manage(self: t.Self, app: Flask) -> None:
        model_class = MagicMock(name="JournalBaseModelMock")
        with app.test_request_context():
            set_current_user("user2@example.test")
            r_query = view_utils.build_query(model_class)
            self.assertIsInstance(r_query, MagicMock)
            model_class.query.filter_by.assert_called_once_with(user=current_user)
            model_class.query.filter_by.return_value.execution_options.assert_called_once_with(
                include_deleted=True
            )

    def test_build_query_user_filters(self: t.Self, app: Flask) -> None:
        model_class = MagicMock(name="JournalBaseModelMock")
        with app.test_request_context():
            set_current_user("user3@example.test")
            r_query = view_utils.build_query(model_class, filters={"id": 1})
            self.assertIsInstance(r_query, MagicMock)
            model_class.query.filter_by.assert_called_once_with(id=1)
            model_class.query.filter_by.return_value.filter_by.assert_called_once_with(
                user=current_user
            )
            model_class.query.filter_by.return_value.filter_by.return_value.execution_options.assert_called_once_with(
                include_deleted=False
            )

    def test_build_query_no_user_admin(self: t.Self, app: Flask) -> None:
        model_class = MagicMock(name="JournalBaseModelMock")
        del model_class.user
        with app.test_request_context():
            set_current_user("user1@example.test")
            r_query = view_utils.build_query(model_class)
            self.assertIsInstance(r_query, MagicMock)
            model_class.query.filter_by.assert_not_called()
            model_class.query.execution_options.assert_called_once_with(
                include_deleted=False
            )

    def test_build_query_no_user_no_admin(self: t.Self, app: Flask) -> None:
        model_class = MagicMock(name="JournalBaseModelMock")
        model_class.configure_mock(__name__="JournalBaseModelMock")
        del model_class.user
        with app.test_request_context():
            set_current_user("user3@example.test")
            self.assertRaises(HTTPException, view_utils.build_query, model_class)
            model_class.query.filter_by.assert_not_called()


class TableViewFunctionTest(UserAppTestBase):
    def setUp(self: t.Self, app: Flask) -> None:
        self.test_table_route = "/tests"

        self.mock_utils: MagicMock = patch("flask_journal.views.base.utils").start()
        self.model_class = MagicMock(name="JournalBaseModel", spec=JournalBaseModel)
        self.model_class.configure_mock(__name__="JournalBaseModelMock")
        self.model_class.side_effect = self._new_model_class

        self.pg_order_query_mock = (
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.return_value
        )
        self.pg_query_mock = (
            self.mock_utils.build_query.return_value.paginate.return_value
        )

        @app.route(self.test_table_route)
        def test() -> None:
            pass

        return super().setUp(app)

    def tearDown(self: t.Self, app: Flask) -> None:
        patch.stopall()
        return super().tearDown(app)

    def _new_model_class(self: t.Self) -> MagicMock:
        return MagicMock(name="JournalBaseModel", spec=JournalBaseModel)

    def _make_table_items(self: t.Self, count: int) -> list[MagicMock]:
        response: list[MagicMock] = []
        for i in range(count):
            m: MagicMock = self.model_class()
            m.configure_mock(id=i, created_at=datetime.now(), deleted_at=None)
            response.append(m)
        return response

    def test_no_results(self: t.Self, app: Flask) -> None:
        self.pg_order_query_mock.items = []

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(self.model_class, endpoint="test")
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_1_result(self: t.Self, app: Flask) -> None:
        test_items = self._make_table_items(1)
        self.pg_order_query_mock.items = test_items
        test_titles = [("id", "Test_ID", 2), ("created_at", "Test Value", 4)]
        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", titles=test_titles
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            for _, name, size in test_titles:
                self.assertIn(html_test_strings["table"]["title"] % (size, name), rv)
            for item in test_items:
                self.assertIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_20_result(self: t.Self, app: Flask) -> None:
        test_items = self._make_table_items(20)
        self.pg_order_query_mock.items = test_items[0:10]
        self.pg_order_query_mock.page = 1
        self.pg_order_query_mock.iter_pages.return_value = [1, 2]
        test_titles = [("id", "Test_ID", 2), ("created_at", "Test Value", 4)]
        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", titles=test_titles
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            for _, name, size in test_titles:
                self.assertIn(html_test_strings["table"]["title"] % (size, name), rv)
            for item in test_items[0:10]:
                self.assertIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            for item in test_items[10:]:
                self.assertNotIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["current_page"] % 1, rv)
            self.assertIn(html_test_strings["table"]["pager"]["other_page"] % 2, rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_20_result_page_2(self: t.Self, app: Flask) -> None:
        test_items = self._make_table_items(20)
        self.pg_order_query_mock.items = test_items[10:]
        self.pg_order_query_mock.page = 2
        self.pg_order_query_mock.iter_pages.return_value = [1, 2]
        test_titles = [("id", "Test_ID", 2), ("created_at", "Test Value", 4)]
        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", titles=test_titles
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            for _, name, size in test_titles:
                self.assertIn(html_test_strings["table"]["title"] % (size, name), rv)
            for item in test_items[0:10]:
                self.assertNotIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            for item in test_items[10:]:
                self.assertIn(
                    html_test_strings["table"]["row"]
                    % (item.id, item.id, item.created_at),
                    rv,
                )
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["current_page"] % 2, rv)
            self.assertIn(html_test_strings["table"]["pager"]["other_page"] % 1, rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )

    def test_order(self: t.Self, app: Flask) -> None:
        self.pg_order_query_mock.items = []

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", order_field="created_at"
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )
            self.mock_utils.build_query.return_value.order_by.assert_called_once_with(
                self.model_class.created_at
            )
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.assert_called_once_with(
                page=1, per_page=10
            )

    def test_order_none(self: t.Self, app: Flask) -> None:
        self.pg_query_mock.items = []

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", order_field=None
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )
            self.mock_utils.build_query.return_value.order_by.assert_not_called()
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.assert_not_called()
            self.mock_utils.build_query.return_value.paginate.assert_called_once_with(
                page=1, per_page=10
            )

    def test_order_invalid_field(self: t.Self, app: Flask) -> None:
        self.pg_query_mock.items = []
        del self.model_class.unknown

        with app.test_request_context(self.test_table_route):
            rv = base_view.table_view(
                self.model_class, endpoint="test", order_field="unknown"
            )
            self.assertIn(html_test_strings["title"] % "Test", rv)
            self.assertIn(html_test_strings["table"]["base"], rv)
            self.assertIn(html_test_strings["table"]["pager"]["form"], rv)
            self.assertIn(
                html_test_strings["table"]["create"] % self.test_table_route, rv
            )
            self.mock_utils.build_query.return_value.order_by.assert_not_called()
            self.mock_utils.build_query.return_value.order_by.return_value.paginate.assert_not_called()
            self.mock_utils.build_query.return_value.paginate.assert_called_once_with(
                page=1, per_page=10
            )

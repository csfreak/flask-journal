import typing as t
from copy import deepcopy
from datetime import datetime
from unittest import TestCase

import wtforms
from flask import Flask
from mock import MagicMock, patch
from werkzeug.exceptions import HTTPException

from flask_journal.forms.base import CustomForm
from flask_journal.models.base import JournalBaseModel
from flask_journal.views import base as base_view
from flask_journal.views import utils as view_utils

from ..base import UserAppTestBase
from ..config import html_test_strings, view_form_action_buttons
from ..utils import set_current_user


class RenderFormFunctionTest(UserAppTestBase):
    def test_invalid_action(self: t.Self, app: Flask) -> None:
        self.assertRaises(
            ValueError,
            base_view.render_form,
            form=base_view.CustomForm(),
            model=JournalBaseModel,
            action='invalid'
        )

    def test_actions(self: t.Self, app: Flask) -> None:
        patch_render_template = patch('flask_journal.views.base.render_template')
        for action in [None, 'view', 'new', 'edit']:
            outer_kwargs = dict(action=action) if action else {}
            with self.subTest(action=action):
                action = action if action else 'view'
                for context_name, context in {
                    'primary_fields_id': {
                        'primary_fields': ['id']
                    },
                    'context_var': {'context_var': 'string'},
                    'none': {}
                }.items():
                    with self.subTest(context=context_name):
                        kwargs = deepcopy(outer_kwargs)
                        kwargs.update(context)
                        form = base_view.CustomForm()
                        primary_fields = context.pop('primary_fields', None)
                        mock_render_template = patch_render_template.start()
                        r: str = base_view.render_form(
                            form=form,
                            model=JournalBaseModel,
                            **kwargs)
                        self.assertEqual(r, mock_render_template.return_value)
                        mock_render_template.assert_called_once_with(
                            'journal/formbase.html',
                            form=form,
                            action=action,
                            primary_fields=primary_fields,
                            title=f"{action} JournalBaseModel",
                            **context)
                        patch_render_template.stop()

    def test_actions_render(self: t.Self, app: Flask) -> None:
        with app.test_request_context():
            set_current_user('user3@example.test')
            for action in [None, 'view', 'new', 'edit']:
                kwargs = dict(action=action) if action else {}
                with self.subTest(action=action):
                    action = action if action else 'view'
                    r: str = base_view.render_form(
                        form=base_view.CustomForm(),
                        model=JournalBaseModel,
                        **kwargs)
                    self.assertNotIn('id="FormPrimaryColumn', r)
                    self.assertNotIn('id="FormSecondaryColumn', r)
                    self.assertIn(html_test_strings['title'].decode() % f"{action.title()} Journalbasemodel", r)
                    for button in view_form_action_buttons[action]:
                        with self.subTest(button=button):
                            self.assertIn(html_test_strings['button'][button], r)
                    for button in [b for b in view_form_action_buttons['all']
                                   if b not in view_form_action_buttons[action]]:
                        with self.subTest(button=button):
                            self.assertNotIn(html_test_strings['button'][button], r)

    def test_columns_render(self: t.Self, app: Flask) -> None:
        with app.test_request_context():
            set_current_user('user3@example.test')
            r: str = base_view.render_form(
                form=base_view.CustomForm(),
                model=JournalBaseModel,
                primary_fields=['id'])
            self.assertIn('id="FormPrimaryColumn', r)
            self.assertIn('id="FormSecondaryColumn', r)

    def test_undelete(self: t.Self, app: Flask) -> None:
        with app.test_request_context():
            set_current_user('user3@example.test')
            r: str = base_view.render_form(
                form=base_view.CustomForm(data={'deleted_at': datetime.now()}),
                model=JournalBaseModel)
            with self.subTest(button='undelete'):
                self.assertIn(html_test_strings['button']['undelete'], r)
            for button in [b for b in view_form_action_buttons['all']
                           if b != 'undelete']:
                with self.subTest(button=button):
                    self.assertNotIn(html_test_strings['button'][button], r)


class FormViewFunctionTest(TestCase):

    def setUp(self: t.Self) -> None:
        self.mock_render_form: MagicMock = patch('flask_journal.views.base.render_form').start()
        self.mock_utils: MagicMock = patch('flask_journal.views.base.utils').start()
        self.mock_redirect: MagicMock = patch('flask_journal.views.base.redirect').start()
        self.mock_db: MagicMock = patch('flask_journal.views.base.db').start()
        self.mock_flash: MagicMock = patch('flask_journal.views.base.flash').start()
        self.mock_abort: MagicMock = patch('flask_journal.views.base.abort').start()
        self.mock_current_user: MagicMock = patch(
            'flask_journal.views.base.current_user',
            new_callable=MagicMock).start()
        self.mock_url_for: MagicMock = patch('flask_journal.views.base.url_for').start()

        self.mock_abort.side_effect = HTTPException()

        self.form_class = MagicMock(name='CustomForm')
        self.model_class = MagicMock(name='JournalBaseModel')
        self.model_class.configure_mock(__name__='JournalBaseModelMock')
        return super().setUp()

    def tearDown(self: t.Self) -> None:
        patch.stopall()
        return super().tearDown()

    def test_id_none_get(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = False
        base_view.form_view(self.model_class, self.form_class, '')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': None})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_render_form.assert_called_once_with(
            action='new', form=self.form_class.return_value, model=self.model_class)
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
        base_view.form_view(self.model_class, self.form_class, '')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_render_form.assert_called_once_with(
            form=self.form_class.return_value, model=self.model_class)
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
            base_view.form_view(self.model_class, self.form_class, '')
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail('abort not called')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(
            model=self.model_class, filters={
                'id': self.mock_utils.process_request_id.return_value})
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
        self.mock_utils.form_submit_action.return_value = 'Create'
        base_view.form_view(self.model_class, self.form_class, '')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': None})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.model_class.assert_called_once_with(user=self.mock_current_user)
        self.form_class.return_value.populate_obj.assert_called_once_with(self.model_class.return_value)
        self.mock_db.session.add.assert_called_once_with(self.model_class.return_value)
        self.mock_db.session.commit.assert_called_once_with()
        self.mock_flash.assert_called_once_with("JournalBaseModelMock Created", category='message')
        self.mock_render_form.assert_called_once_with(form=self.form_class.return_value, model=self.model_class)
        self.mock_redirect.assert_not_called()
        self.mock_abort.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_id_set_create(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = 'Create'
        try:
            base_view.form_view(self.model_class, self.form_class, '')
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail('abort not called')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
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
        self.mock_utils.form_submit_action.return_value = 'Update'
        base_view.form_view(self.model_class, self.form_class, '')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.form_class.return_value.process.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.populate_obj.assert_called_once_with(
            self.mock_utils.build_query.return_value.first.return_value)
        self.mock_db.session.add.assert_called_once_with(self.mock_utils.build_query.return_value.first.return_value)
        self.mock_db.session.commit.assert_called_once_with()
        self.mock_flash.assert_called_once_with("JournalBaseModelMock Updated", category='message')
        self.mock_render_form.assert_called_once_with(form=self.form_class.return_value, model=self.model_class)
        self.mock_redirect.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_none_update(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = 'Update'
        try:
            base_view.form_view(self.model_class, self.form_class, '')
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail('abort not called')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
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
        self.mock_utils.form_submit_action.return_value = 'Edit'
        base_view.form_view(self.model_class, self.form_class, '')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_render_form.assert_called_once_with(
            action='edit', form=self.form_class.return_value, model=self.model_class)
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
        self.mock_utils.form_submit_action.return_value = 'Edit'
        try:
            base_view.form_view(self.model_class, self.form_class, '')
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail('abort not called')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
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
        self.mock_utils.form_submit_action.return_value = 'Delete'
        base_view.form_view(self.model_class, self.form_class, 'test_endpoint')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_utils.build_query.return_value.first.return_value.delete.assert_called_once_with()
        self.mock_db.session.add.assert_called_once_with(self.mock_utils.build_query.return_value.first.return_value)
        self.mock_db.session.commit.assert_called_once_with()
        self.mock_flash.assert_called_once_with("JournalBaseModelMock Deleted")
        self.mock_url_for.assert_called_once_with('test_endpoint')
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
        self.mock_utils.form_submit_action.return_value = 'Delete'
        try:
            base_view.form_view(self.model_class, self.form_class, '')
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail('abort not called')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
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
        self.mock_utils.form_submit_action.return_value = 'Undelete'
        self.mock_current_user.has_role.return_value = True
        base_view.form_view(self.model_class, self.form_class, 'test_endpoint')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_current_user.has_role.assert_called_once_with('manage')
        self.mock_utils.build_query.return_value.first.return_value.undelete.assert_called_once_with()
        self.mock_db.session.add.assert_called_once_with(self.mock_utils.build_query.return_value.first.return_value)
        self.mock_db.session.commit.assert_called_once_with()
        self.form_class.return_value.process.assert_called_once_with(
            obj=self.mock_utils.build_query.return_value.first.return_value)
        self.mock_flash.assert_called_once_with("JournalBaseModelMock Restored", category='warning')
        self.mock_render_form.assert_called_once_with(form=self.form_class.return_value, model=self.model_class)
        self.form_class.return_value.populate_obj.assert_not_called()
        self.mock_redirect.assert_not_called()
        self.mock_abort.assert_not_called()
        self.model_class.assert_not_called()
        self.mock_url_for.assert_not_called()

    def test_obj_none_undelete(self: t.Self) -> None:
        self.mock_utils.process_request_id.return_value = 1
        self.mock_utils.build_query.return_value.first.return_value = None
        self.form_class.return_value.validate_on_submit.return_value = True
        self.mock_utils.form_submit_action.return_value = 'Undelete'
        try:
            base_view.form_view(self.model_class, self.form_class, '')
        except HTTPException:
            self.mock_abort.assert_called_once_with(404)
        else:
            self.fail('abort not called')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
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
        self.mock_utils.form_submit_action.return_value = 'Undelete'
        self.mock_current_user.has_role.return_value = False
        base_view.form_view(self.model_class, self.form_class, '')
        self.mock_utils.process_request_id.assert_called_once_with()
        self.mock_utils.build_query.assert_called_once_with(model=self.model_class, filters={'id': 1})
        self.mock_utils.build_query.return_value.first.assert_called_once_with()
        self.form_class.assert_called_once_with(obj=self.mock_utils.build_query.return_value.first.return_value)
        self.form_class.return_value.validate_on_submit.assert_called_once_with()
        self.mock_current_user.has_role.assert_called_once_with('manage')
        self.model_class.assert_not_called()
        self.form_class.return_value.populate_obj.assert_not_called()
        self.form_class.return_value.process.assert_not_called()
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_not_called()
        self.mock_abort.assert_not_called()
        self.mock_flash.assert_called_once_with('Unable to Undelete JournalBaseModelMock', category='error')
        self.mock_render_form.assert_called_once_with(form=self.form_class.return_value, model=self.model_class)
        self.mock_redirect.assert_not_called()
        self.mock_url_for.assert_not_called()


class ViewUtilsFunctionTest(UserAppTestBase):
    def test_process_request_id_none(self: t.Self, app: Flask) -> None:
        with app.test_request_context():
            set_current_user('user1@example.test')
            r_id: int | None = view_utils.process_request_id()
            self.assertIsNone(r_id)

    def test_process_request_id_arg(self: t.Self, app: Flask) -> None:
        with app.test_request_context(query_string={'id': '1'}):
            set_current_user('user1@example.test')
            r_id: int | None = view_utils.process_request_id()
            self.assertIsInstance(r_id, int)
            self.assertEqual(r_id, 1)

    def test_process_request_id_form(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method='POST', data={'id': '1'}):
            set_current_user('user1@example.test')
            r_id: int | None = view_utils.process_request_id()
            self.assertIsInstance(r_id, int)
            self.assertEqual(r_id, 1)

    def test_process_request_id_both(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method='POST', data={'id': '1'}, query_string={'id': '2'}):
            r_id: int | None = view_utils.process_request_id()
            self.assertIsInstance(r_id, int)
            self.assertEqual(r_id, 1)

    def test_form_submit_action_no_submit(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method='GET', data={'id': '1'}):
            form = CustomForm()
            self.assertRaises(ValueError, view_utils.form_submit_action, form)

    def test_form_submit_action_submit_no_button(self: t.Self, app: Flask) -> None:
        with app.test_request_context(method='POST', data={'id': '1'}):
            form = CustomForm()
            self.assertRaises(ValueError, view_utils.form_submit_action, form)

    def test_form_submit_action(self: t.Self, app: Flask) -> None:
        class TestForm(CustomForm):
            custom = wtforms.fields.BooleanField(name='Custom', widget=wtforms.widgets.SubmitInput)

        for action in ['Create', 'Edit', 'Update', 'Delete', 'Undelete', 'Custom']:
            with self.subTest(action=action):
                expected: str = action
                with app.test_request_context(method='POST', data={'id': '1', expected: expected}):
                    form = TestForm()
                    r_action: str = view_utils.form_submit_action(form)
                    self.assertEqual(r_action, expected)

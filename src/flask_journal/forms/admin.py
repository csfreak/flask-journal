import typing as t

from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, SelectField, StringField, SubmitField
from wtforms.validators import Length

from ..models import Role
from ..views.themes import Theme
from .base import CustomForm, UnmanagedForm
from .fields import (
    DisplayDateTimeField,
    DisplayStringField,
    ModelSelectMultipleField,
    ReadOnlyFormField,
    UserSettingsField,
)


class UserTrackingForm(UnmanagedForm):
    last_login_at = DisplayDateTimeField(name="Last Login At")
    last_login_ip = DisplayStringField(name="Last Login IP")
    current_login_at = DisplayDateTimeField(name="Current Login At")
    current_login_ip = DisplayStringField(name="Current Login IP")
    login_count = DisplayStringField(name="Login Count")


class UserSettingsSubForm(FlaskForm):
    theme = SelectField(name="Theme", choices=list(Theme), default="default")
    home_tags = BooleanField("Show Tag Cloud on Home Screen")
    home_preview = BooleanField("Show Entry Previews on Home Screen")


class UserSettingsForm(UserSettingsSubForm):
    submit = SubmitField(name="Update")


class UserForm(CustomForm):
    email = EmailField(name="Email")
    name = StringField(name="Name")
    confirmed_at = DisplayDateTimeField(name="Confirmed At")
    roles = ModelSelectMultipleField(name="Roles", model=Role)
    tracking = ReadOnlyFormField(UserTrackingForm, name="Tracking", label="Logins")
    settings = UserSettingsField(
        UserSettingsSubForm, name="Settings", label="User Settings"
    )

    def populate_obj(self: t.Self, obj: User) -> None:
        for name, field in self._fields.items():
            if name == "email" and field.data != obj.email:
                obj.confirmed_at = None
        return super().populate_obj(obj)


class RoleForm(CustomForm):
    name = StringField(name="Name", validators=[Length(max=64)])
    description = StringField(name="Description")

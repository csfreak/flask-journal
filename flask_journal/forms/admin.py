from flask_wtf import FlaskForm
from wtforms import EmailField, SelectField, StringField, SubmitField
from wtforms.validators import Length

from ..views.themes import Theme
from .base import CustomForm, UnmanagedForm
from .fields import (
    DisplayDateTimeField,
    DisplayStringField,
    ReadOnlyFormField,
    RoleField,
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


class UserSettingsForm(UserSettingsSubForm):
    submit = SubmitField(name="Update")


class UserForm(CustomForm):
    email = EmailField(name="Email")
    confirmed_at = DisplayDateTimeField(name="Confirmed At")
    roles = RoleField(name="Roles")
    tracking = ReadOnlyFormField(UserTrackingForm, name="Tracking", label="Logins")
    settings = UserSettingsField(
        UserSettingsSubForm, name="Settings", label="User Settings"
    )


class RoleForm(CustomForm):
    name = StringField(name="Name", validators=[Length(max=64)])
    description = StringField(name="Description")

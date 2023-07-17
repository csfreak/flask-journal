from datetime import datetime

from wtforms import (BooleanField, EmailField, FormField, PasswordField,
                     StringField)
from wtforms.validators import Length

from .base import CustomForm, UnmanagedForm
from .fields import DisplayDateTimeField, DisplayStringField, RoleField


class UserTrackingForm(UnmanagedForm):
    last_login_at = DisplayDateTimeField(name="Last Login At")
    last_login_ip = DisplayStringField(name="Last Login IP")
    current_login_at = DisplayDateTimeField(name="Current Login At")
    current_login_ip = DisplayStringField(name="Current Login IP")
    login_count = DisplayStringField(name='Login Count')


class UserSettingsForm(UnmanagedForm):
    encrypt_entries = BooleanField(name="Encrypt Entries")
    encryption_key = PasswordField(name="Encryption Key")


class UserForm(CustomForm):
    email = EmailField(name="Email")
    confirmed_at = DisplayDateTimeField(name="Confirmed At")
    roles = RoleField(name='Roles')
    tracking = FormField(UserTrackingForm, name="Tracking", label="Logins")
    settings = FormField(UserSettingsForm, name="Settings",
                         label="User Settings")


class RoleForm(CustomForm):
    name = StringField(name="Name", validators=[Length(max=64)])
    description = StringField(name="Description")

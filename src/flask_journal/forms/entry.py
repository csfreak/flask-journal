from datetime import datetime

from flask_security import current_user
from wtforms import BooleanField, StringField, TextAreaField
from wtforms.validators import Length

from ..models import User
from .base import CustomForm
from .fields import ModelSelectMultipleField, TagField


class EntryForm(CustomForm):
    title = StringField(
        name="Title",
        validators=[Length(max=64)],
        default=f"Journal Entry - {datetime.now().date()}",
    )
    content = TextAreaField(name="Body")
    tags = TagField(name="Tags")
    encrypted = BooleanField()
    public = BooleanField()
    shared_with = ModelSelectMultipleField(
        name="Shared With", model=User, exclude=current_user
    )

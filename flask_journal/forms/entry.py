from datetime import datetime

from wtforms import BooleanField, StringField, TextAreaField
from wtforms.validators import Length

from .base import CustomForm
from .fields import TagField


class EntryForm(CustomForm):
    title = StringField(
        name="Title",
        validators=[Length(max=64)],
        default=f"Journal Entry - {datetime.now().date()}",
    )
    content = TextAreaField(name="Body")
    tags = TagField(name="Tags")
    encrypted = BooleanField()

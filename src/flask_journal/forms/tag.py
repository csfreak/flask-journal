from wtforms import StringField
from wtforms.validators import Length

from .base import CustomForm


class TagForm(CustomForm):
    name = StringField(name="Name", validators=[Length(max=64)])

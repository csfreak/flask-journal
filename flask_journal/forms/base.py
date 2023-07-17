import typing as t

from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField

from ..models import db
from ..models.base import JournalBaseModel
from .fields import DisplayDateTimeField


class CustomForm(FlaskForm):
    id = HiddenField()
    created_at = DisplayDateTimeField(name="Created At")
    updated_at = DisplayDateTimeField(name="Updated At")
    deleted_at = DisplayDateTimeField(name="Deleted At")
    update = SubmitField(name="Update")
    edit = SubmitField(name="Edit")
    create = SubmitField(name="Create")
    delete = SubmitField(name="Delete")
    undelete = SubmitField(name="Undelete")

    def populate_obj(self: t.Self, obj: JournalBaseModel) -> None:
        for name, field in self._fields.items():
            if name not in obj.immutable_attrs and field.type != 'SubmitField':
                field.populate_obj(obj, name)
        db.session.add(obj)
        db.session.commit()


class UnmanagedForm(FlaskForm):
    def populate_obj(self: t.Self, obj: JournalBaseModel) -> None:
        pass

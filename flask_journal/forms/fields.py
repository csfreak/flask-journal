import typing as t

from flask import flash
from flask_login import current_user
from wtforms import DateTimeField, StringField

from ..models import Role, Tag, db
from .widgets import PlainTextWidget


class DisplayDateTimeField(DateTimeField):
    widget = PlainTextWidget()

    def process_formdata(self: t.Self, *args, **kwargs):
        pass

    def populate_obj(self: t.Self, *args, **kwargs):
        pass

    def _value(self: t.Self) -> str:
        return self.data and self.data.strftime(self.format[0]) or ""


class DisplayStringField(StringField):
    widget = PlainTextWidget()

    def process_formdata(self: t.Self, *args, **kwargs):
        pass

    def populate_obj(self: t.Self, *args, **kwargs):
        pass


class TagField(StringField):

    def process_formdata(self, valuelist: list[str]):
        if valuelist:
            self.data: list[Tag] = []
            for tag in valuelist[0].split(' '):
                if tag.strip() == '':
                    continue
                obj = Tag.query.filter_by(name=tag, user=current_user).first()
                if not obj:
                    obj = Tag(user=current_user, name=tag)
                    db.session.add(obj)
                self.data.append(obj)

    def _value(self):
        return " ".join([tag.name for tag in self.data]) if self.data is not None else ""


class RoleField(StringField):
    def process_formdata(self, valuelist: list[str]):
        if valuelist:
            self.data: list[Role] = []
            for role in valuelist[0].split(' '):
                if role.strip() == '':
                    continue
                obj = Role.query.filter_by(name=role).first()
                if not obj:
                    flash(f"Invalid Role {role}")
                self.data.append(obj)

    def _value(self):
        return " ".join([role.name for role in self.data]) if self.data is not None else ""

import logging
import typing as t

from flask_login import current_user
from wtforms import DateTimeField, Form, FormField, StringField
from wtforms.validators import ValidationError

from ..models import Role, Tag, User, UserSettings, db
from .widgets import PlainTextWidget

logger = logging.getLogger(__name__)


class DisplayDateTimeField(DateTimeField):
    widget = PlainTextWidget()

    def process_formdata(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

    def populate_obj(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

    def validate(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        return True

    def _value(self: t.Self) -> str:
        return self.data and self.data.strftime(self.format[0]) or ""


class DisplayStringField(StringField):
    widget = PlainTextWidget()

    def process_formdata(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

    def populate_obj(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

    def validate(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:  # pragma: no cover
        return True


class TagField(StringField):

    def process_formdata(self: t.Self, valuelist: list[str]) -> None:
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

    def _value(self: t.Self) -> str:
        return " ".join([tag.name for tag in self.data]) if self.data is not None else ""


class RoleField(StringField):
    def process_formdata(self: t.Self, valuelist: list[str]) -> None:
        if valuelist:
            self.data: list[Role] = []
            for role in valuelist[0].split(' '):
                if role.strip() == '':
                    continue
                obj = Role.query.filter_by(name=role).first()
                if obj is not None:
                    self.data.append(obj)
        else:  # pragma: no cover
            pass

    def _value(self: t.Self) -> str:
        return " ".join([role.name for role in self.data]) if self.data is not None else ""

    def pre_validate(self: t.Self, form: Form) -> None:
        raw_role_names = self.raw_data[0].split(' ')
        processed_role_names = [role.name for role in self.data]
        invalid_role_names = []
        for raw_name in raw_role_names:
            if raw_name and raw_name not in processed_role_names:
                invalid_role_names.append(raw_name)
        if len(invalid_role_names) != 0:
            logger.error("found invalid role(s): %s", ' '.join(invalid_role_names))
            logger.debug("comparing %s to %s", raw_role_names, processed_role_names)
            raise ValidationError("invalid role(s): %s" % ' '.join(invalid_role_names))


class UserSettingsField(FormField):
    def populate_obj(self: t.Self, obj: User, name: str) -> None:
        candidate = getattr(obj, name, None)
        if candidate is None:  # pragma: no cover
            if self._obj is None:
                candidate = UserSettings(user=obj)
            else:
                candidate = self._obj
        self.form.populate_obj(candidate)
        setattr(obj, name, candidate)


class ReadOnlyFormField(FormField):
    def validate(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        return True

    def populate_obj(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

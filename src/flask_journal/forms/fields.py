import logging
import typing as t

from flask_login import current_user
from flask_wtf import FlaskForm
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from wtforms import DateTimeField, FormField, SelectFieldBase, StringField, widgets
from wtforms.validators import ValidationError

from ..models import Tag, User, UserSettings, db
from ..models.base import JournalBaseModel
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

    def validate(
        self: t.Self, *args: t.Any, **kwargs: t.Any
    ) -> None:  # pragma: no cover
        return True


class TagField(StringField):
    def process_formdata(self: t.Self, valuelist: list[str]) -> None:
        if valuelist:
            self.data: list[Tag] = []
            for tag in valuelist[0].split(" "):
                if tag.strip() == "":
                    continue
                obj = db.session.scalar(
                    select(Tag)
                    .filter_by(name=tag, user=current_user)
                    .options(joinedload(Tag.entries))
                )

                if not obj:
                    obj = Tag(user=current_user, name=tag)
                self.data.append(obj)

    def _value(self: t.Self) -> str:
        return (
            " ".join([tag.name for tag in self.data]) if self.data is not None else ""
        )

    def populate_obj(self: t.Self, obj: JournalBaseModel, name: str) -> None:
        """
        Populates `obj.<name>` with the field's data.

        :note: This is a destructive operation. If `obj.<name>` already exists,
               it will be overridden. Use with caution.
        """
        obj.tags = []
        if isinstance(self.data, list):
            for item in self.data:
                obj.tags.append(item)
                db.session.add(item)
        else:
            obj.tags.append(self.data)


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


class ModelSelectField(SelectFieldBase):
    widget = widgets.Select()

    def __init__(
        self: t.Self,
        label: str = None,
        validators: callable = None,
        model: JournalBaseModel = None,
        exclude: JournalBaseModel | list[JournalBaseModel] = None,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(label, validators, **kwargs)
        self.model = model
        self.excludes = []
        if exclude:
            try:
                self.excludes.extend(exclude)
            except TypeError:
                self.excludes.append(exclude)


class ModelSelectMultipleField(ModelSelectField):
    widget = widgets.Select(multiple=True)

    def iter_choices(
        self: t.Self,
    ) -> t.Generator[tuple[str, str, bool, dict], None, None]:
        instances = db.session.scalars(select(self.model))
        for instance in instances:
            if instance not in self.excludes:
                yield (
                    instance.id,
                    str(instance),
                    self.data is not None and instance in self.data,
                    dict(),
                )

    def process_data(self: t.Self, value: t.Any) -> None:
        self.data = (
            [instance for instance in value if isinstance(instance, self.model)]
            if value
            else []
        )

    def process_formdata(self: t.Self, valuelist: t.Any) -> None:
        if not valuelist:
            self.data = []
            return
        try:
            self.data = [self.model.find_by_id(value) for value in valuelist]
        except ValueError as exc:
            raise ValueError(self.gettext("Invalid Choice: could not coerce.")) from exc

    def pre_validate(self: t.Self, form: FlaskForm) -> None:
        if self.data is None:
            return
        acceptable = {c[0] for c in self.iter_choices()}
        if any(
            not (isinstance(d, self.model) and d.id in acceptable) for d in self.data
        ):
            raise ValidationError("Invalid Value(s)")

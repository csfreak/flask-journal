import logging
import typing as t

from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField

from ..models import db
from ..models.base import JournalBaseModel
from .fields import DisplayDateTimeField

logger = logging.getLogger(__name__)


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

    def __init__(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        self.__name__ = type(self).__name__
        super().__init__(*args, **kwargs)

    def populate_obj(self: t.Self, obj: JournalBaseModel) -> None:
        for name, field in self._fields.items():
            if name not in obj.immutable_attrs and field.type != "SubmitField":
                field.populate_obj(obj, name)
        db.session.add(obj)
        db.session.commit()

    def validate_on_submit(
        self: t.Self, extra_validators: dict[str, t.Callable] | None = None
    ) -> bool:
        """Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.

        :param extra_validators:
            If provided, is a dict mapping field names to a sequence of
            callables which will be passed as extra validators to the field's
            `validate` method.

        Returns `True` if ``is_submitted()`` and ``validate()`` no errors occur.
        """

        if not self.is_submitted():
            logger.debug("form not submitted")
            return False

        if not self.validate(extra_validators=extra_validators):
            logger.debug("form validation failed: %s", self.errors)
            return False

        return True


class UnmanagedForm(FlaskForm):
    def populate_obj(self: t.Self, obj: JournalBaseModel) -> None:
        pass

    def validate(self: t.Self, *args: t.Any, **kwargs: t.Any) -> None:
        pass

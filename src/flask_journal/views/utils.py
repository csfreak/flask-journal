import logging
import typing as t

from flask import abort, flash, request
from flask_security import current_user
from sqlalchemy import Select, select
from wtforms.fields import SubmitField

from flask_journal.forms.base import CustomForm
from flask_journal.models.base import JournalBaseModel

logger = logging.getLogger(__name__)


def process_request_id() -> int | None:
    id: int | None = None
    if "id" in request.form.keys():
        id = request.form.get("id", type=int)
        logger.debug("found id %d in form data", id)
    else:
        id = request.args.get("id", None, type=int)
        if id:
            logger.debug("found id %d in args", id)
        else:
            logger.debug("id not found")
    return id


def build_select(
    model: JournalBaseModel,
    filters: dict[str, t.Any] | None = None,
    shared: bool | None = None,
) -> Select:
    include_deleted: bool = (
        True if current_user.has_role("manage") else False  # pyright: ignore
    )
    stmt: Select = select(model)
    if filters is not None:
        stmt = stmt.filter_by(**filters)

    match (model.ownable, model.shareable, shared):
        case (True, True, None):
            stmt = stmt.where(
                (model.user == current_user)
                | (model.shared_with.any(model.shared_with.contains(current_user)))
            )

        case (True, True, True):
            stmt = stmt.where(
                (model.shared_with.any(model.shared_with.contains(current_user)))
            )

        case (False, False, _):
            if not current_user.has_role("admin"):
                flash(f"Unable to Access Resource {model.__name__}")
                return abort(403)

        case _:
            stmt = stmt.filter_by(user=current_user)

    stmt = stmt.execution_options(include_deleted=include_deleted)
    return stmt


def form_submit_action(form: CustomForm) -> str:
    """Returns the name of the form SubmitField that was used to submit form.

    Args:
        form (CustomForm): Form that was submitted

    Returns:
        str: name of SubmitField used
    """

    if not form.is_submitted():
        logger.error("form was not submitted: %s" % form.__name__)
        raise ValueError("form was not submitted: %s" % form.__name__)

    # Check for SubmitFields
    for field in form:
        if isinstance(field, SubmitField) and field.data:
            logger.debug("field SubmitField.%s found", field.name)
            return field.name

    # Finding Other Fields if not SubmitField found
    for field in form:
        if (
            hasattr(field.widget, "input_type")
            and field.widget.input_type == "submit"
            and field.data
        ):
            logger.debug("field %s.%s found", field.type, field.name)
            return field.name

    logger.error("form wasn't submitted with a Field: %s" % form.__name__)
    raise ValueError("form wasn't submitted with a Field: %s" % form.__name__)

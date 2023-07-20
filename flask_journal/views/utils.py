
import typing as t

from flask import abort, flash, request
from flask_security import current_user
from flask_sqlalchemy.query import Query
from wtforms.fields import SubmitField

from flask_journal.forms.base import CustomForm
from flask_journal.models.base import JournalBaseModel


def process_request_id() -> int | None:
    id: int | None = None
    if 'id' in request.form.keys():
        id = request.form.get('id', type=int)
    else:
        id = request.args.get('id', None, type=int)

    return id


def build_query(model: JournalBaseModel, filters: dict[str, t.Any] | None = None) -> Query:
    include_deleted: bool = True if current_user.has_role(  # pyright: ignore
        'manage') else False
    query: Query = model.query
    if filters is not None:
        query = query.filter_by(**filters)
    if hasattr(model, 'user'):
        query = query.filter_by(user=current_user)
    elif not current_user.has_role('admin'):  # pyright: ignore
        flash(f"Unable to Access Resource {model.__name__}")
        return abort(403)
    query = query.execution_options(
        include_deleted=include_deleted)

    return query


def form_submit_action(form: CustomForm) -> str:
    """Returns the name of the form SubmitField that was used to submit form.

    Args:
        form (CustomForm): Form that was submitted

    Returns:
        str: name of SubmitField used
    """

    if not form.is_submitted():
        raise ValueError("form was not submitted: %s" % form)

    # Check for SubmitFields
    for field in form:
        if isinstance(field, SubmitField) and field.data:
            return field.name

    # Finding Other Fields if not SubmitField found
    for field in form:
        if hasattr(field.widget, 'input_type') and \
                field.widget.input_type == 'submit' and field.data:
            return field.name

    raise ValueError("form wasn't submitted with a Field: %s" % form)

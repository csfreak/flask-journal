import logging
import typing as t

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import Select
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.sql import ColumnExpressionArgument, desc

from ..forms import CustomForm
from ..models import db
from ..models.base import JournalBaseModel
from . import utils, werkzeugResponse

logger = logging.getLogger(__name__)


def render_form(
    form: CustomForm,
    model: JournalBaseModel,
    primary_fields: list[str] = None,
    action: str = "view",
    **context: t.Any,
) -> str:
    logger.debug(
        "render form %s for model %s with data %s",
        form.__name__,
        model.__name__,
        form.data,
    )
    if action not in ["new", "view", "edit"]:
        logger.error("action %s not allowed" % action)
        raise ValueError("action must be new, view, or edit")
    return render_template(
        "journal/formbase.html",
        form=form,
        action=action,
        primary_fields=primary_fields,
        title=f"{action} {model.__name__}",
        **context,
    )


def form_view(
    model: JournalBaseModel,
    form_class: type[CustomForm],
    table_view: str,
    defaults: dict[str, t.Any] = None,
    id: int | None = None,
    **context: t.Any,
) -> werkzeugResponse | str:
    logger.debug("form view for model %s", model.__name__)
    if id is None:
        id = utils.process_request_id()
    context.setdefault("action", "view")
    context.setdefault("readonly", False)
    context.setdefault("model", model)
    select: Select = utils.build_select(model=model, filters=dict(id=id))
    obj: JournalBaseModel = db.session.scalar(select)

    if obj is None:
        logger.debug("No %s loaded by query", model.__name__)
    elif obj.ownable and obj.user != current_user:
        context.update(dict(readonly=True))

    form = form_class(obj=obj)
    context["form"] = form
    message: str = model.__name__
    category: str = "message"
    if form.validate_on_submit():
        logger.debug("form submit validated with data %s", form.data)
        match utils.form_submit_action(form):
            case "Create" if id is None:
                if defaults is None:
                    defaults = dict()
                if hasattr(model, "user"):
                    defaults["user"] = current_user
                obj = model(**defaults)
                form.populate_obj(obj)
                # Reload form data from object to populate DB created values in display
                form.process(obj=obj, formdata=None)
                db.session.commit()
                id = obj.id
                message = f"{message} Created"
            case "Update" if obj:
                form.populate_obj(obj)
                # Reload form data from object to populate DB created values in display
                form.process(obj=obj, formdata=None)
                db.session.commit()
                message = f"{message} Updated"
            case "Edit" if obj:
                context["action"] = "edit"
            case "Delete" if obj:
                obj.delete()
                db.session.add(obj)
                db.session.commit()
                flash(f"{message} Deleted")
                return redirect(url_for(table_view))
            case "Undelete" if obj and current_user.has_role("manage"):
                obj.undelete()
                db.session.add(obj)
                db.session.commit()
                form.process(obj=obj)
                message = f"{message} Restored"
                category = "warning"
            case form_action:
                message = f"Unable to {form_action} {message}"
                category = "error"

    if id is None:
        context["action"] = "new"
    elif obj is None:
        abort(404)
    if message != model.__name__ or category != "message":
        logger.debug("flash message %s with category %s", message, category)
        flash(message, category=category)
    return render_form(**context)


def table_view(
    model: JournalBaseModel,
    titles: list[tuple[str, str, int]] | None = None,
    order_field: str = "created_at",
    descending: bool = False,
    endpoint: str = "",
    shared: bool | None = None,
) -> werkzeugResponse | str:
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)

    select: Select = utils.build_select(model=model, shared=shared)

    if order_field and hasattr(model, order_field):
        order_attr: QueryableAttribute = getattr(model, order_field)
        order_exp: ColumnExpressionArgument = (
            desc(order_attr) if descending else order_attr
        )
        select: Select = select.order_by(order_exp)

    pagination: Pagination = db.paginate(select, page=page, per_page=page_size)
    return render_template(
        "journal/tablebase.html",
        pagination=pagination,
        titles=titles,
        endpoint=endpoint,
        title=request.endpoint.split(".")[-1],
    )

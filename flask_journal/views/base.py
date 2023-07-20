import typing as t

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_sqlalchemy.pagination import Pagination
from flask_sqlalchemy.query import Query
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.sql import ColumnExpressionArgument, desc

from ..forms import CustomForm
from ..models import db
from ..models.base import JournalBaseModel
from . import utils, werkzeugResponse


def render_form(form: CustomForm,
                model: JournalBaseModel,
                primary_fields: list[str] | None = None,
                action: str = 'view',
                **context: t.Any) -> str:

    if action not in ['new', 'view', 'edit']:
        raise ValueError("action must be view or edit")
    return render_template(
        'journal/formbase.html',
        form=form,
        action=action,
        primary_fields=primary_fields,
        title=f"{action} {model.__name__}",
        **context
    )


def form_view(
        model: JournalBaseModel,
        form_class: type[CustomForm],
        table_view: str,
        **context: t.Any) -> werkzeugResponse | str:

    id = utils.process_request_id()

    query: Query = utils.build_query(model=model, filters=dict(id=id))

    obj: JournalBaseModel = query.first()
    form = form_class(obj=obj)
    context.update(dict(form=form, model=model))
    message: str = model.__name__
    category: str = 'message'
    if form.validate_on_submit():
        match utils.form_submit_action(form):
            case 'Create' if id is None:
                obj = model(user=current_user)
                form.populate_obj(obj)
                db.session.add(obj)
                db.session.commit()
                form.process(obj=obj)
                id = obj.id
                message = f"{message} Created"
            case 'Update' if obj:
                form.populate_obj(obj)
                db.session.add(obj)
                db.session.commit()
                form.process(obj=obj)
                message = f"{message} Updated"
            case 'Edit' if obj:
                context['action'] = 'edit'
            case 'Delete' if obj:
                obj.delete()
                db.session.add(obj)
                db.session.commit()
                flash(f"{message} Deleted")
                return redirect(url_for(table_view))
            case 'Undelete' if obj and current_user.has_role('manage'):
                obj.undelete()
                db.session.add(obj)
                db.session.commit()
                form.process(obj=obj)
                message = f"{message} Restored"
                category = 'warning'
            case form_action:
                message = f"Unable to {form_action} {message}"
                category = 'error'

    if id is None:
        context['action'] = 'new'
    elif obj is None:
        abort(404)
    if message != model.__name__ or category != 'message':
        flash(message, category=category)
    return render_form(**context)


def table_view(model: JournalBaseModel,
               titles: list[tuple[str, str, int]] | None = None,
               order_field: str = 'created_at',
               descending: bool = False,
               include_deleted: bool | None = None,
               endpoint: str = '') -> werkzeugResponse | str:
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    if include_deleted is None:
        include_deleted = True if current_user.has_role(  # pyright: ignore
            'manage') else False

    query: Query = model.query
    if hasattr(model, 'user'):
        query = query.filter_by(user=current_user)
    elif not current_user.has_role('admin'):  # pyright: ignore
        flash(f"Unable to Access Resource {model}")
        return redirect('.index')
    query: Query = query.execution_options(include_deleted=include_deleted)

    if order_field and hasattr(model, order_field):
        order_attr: QueryableAttribute = getattr(model, order_field)
        order_exp: ColumnExpressionArgument = desc(
            order_attr) if descending else order_attr
        query: Query = query.order_by(order_exp)

    pagination: Pagination = query.paginate(page=page, per_page=page_size)
    return render_template('journal/tablebase.html',
                           pagination=pagination,
                           titles=titles,
                           endpoint=endpoint,
                           title=request.endpoint.split('.')[-1])

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_sqlalchemy.pagination import Pagination
from flask_sqlalchemy.query import Query
from sqlalchemy.orm.attributes import QueryableAttribute
from sqlalchemy.sql import ColumnExpressionArgument, desc

from ..forms import CustomForm
from ..models import db
from ..models.base import JournalBaseModel
from . import werkzeugResponse
from .utils import process_request_id


def render_form(form: CustomForm,
                model: JournalBaseModel,
                primary_fields: list[str] | None = None,
                action: str = 'view',
                **context) -> str:

    if action not in ['new', 'view', 'edit']:
        raise ValueError("action must be view or edit")
    return render_template(
        'journal/formbase.html',
        form=form,
        action=action,
        primary_fields=primary_fields,
        title=f"{action} {model.__name__}".capitalize(),
        **context
    )


def form_view(model: JournalBaseModel, form_class: type[CustomForm], table_view: str, primary_fields: list[str] | None = None) -> werkzeugResponse | str:
    id = process_request_id()
    include_deleted: bool = True if current_user.has_role(  # pyright: ignore
        'manage') else False
    query: Query = model.query.filter_by(id=id)
    if hasattr(model, 'user'):
        query = query.filter_by(user=current_user)
    elif not current_user.has_role('admin'):  # pyright: ignore
        flash(f"Unable to Access Resource {model}")
        return redirect('.index')
    query = query.execution_options(
        include_deleted=include_deleted)
    obj: JournalBaseModel = query.first()  # pyright: ignore
    form = form_class(obj=obj)

    if form.validate_on_submit():
        if form.create.data:
            obj = model(user=current_user)
        if form.update.data or form.create.data:
            form.populate_obj(obj)
            db.session.add(obj)
            db.session.commit()
            form.process(obj=obj)
            flash(
                f"{model.__name__} {'Updated' if form.update.data else 'Created'} Successfully")
            return render_form(form=form, primary_fields=primary_fields, model=model)
        elif form.edit.data:
            return render_form(form=form, primary_fields=primary_fields, action='edit', model=model)
        elif form.delete.data:
            if obj:
                flash(f"Deleted {obj}")
                obj.delete()
                db.session.add(obj)
                db.session.commit()
                return redirect(url_for(table_view))
            flash("Delete Failed", category='error')
        elif form.undelete.data:
            if obj:
                flash(f"Restore {obj}")
                obj.undelete()
                db.session.add(obj)
                db.session.commit()
                form.process(obj=obj)
                return render_form(form=form, primary_fields=primary_fields)
            flash("Delete Failed", category='error')
    if id is None:
        return render_form(form=form, primary_fields=primary_fields, action='new', model=model)
    return render_form(form=form, primary_fields=primary_fields, model=model)


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
                           title=request.endpoint.split('.')[-1].capitalize())

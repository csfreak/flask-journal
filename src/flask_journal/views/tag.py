from flask import render_template
from flask_login import login_required

from ..forms import TagForm
from ..models import Tag
from . import bp, utils, werkzeugResponse
from .base import form_view, table_view


@bp.route("/tags")
@login_required
def tags() -> werkzeugResponse | str:
    return table_view(
        Tag,
        titles=[("id", "#", 1), ("name", "Name", 3), ("created_at", "Created At", 2)],
        order_field="name",
        endpoint=".tag",
    )


@bp.route("/tag", methods=["GET", "POST"])
@bp.route("/tag/<int:id>", methods=["GET", "POST"])
@login_required
def tag(id: int | None = None) -> werkzeugResponse | str:
    return form_view(
        model=Tag,
        form_class=TagForm,
        primary_fields=["Name"],
        table_view=".tags",
        id=id,
    )


@bp.route("/tag/<int:id>/entries")
def tag_entries(id: int) -> werkzeugResponse | str:
    tag = utils.build_query(model=Tag, filters=dict(id=id)).first()
    return render_template(
        "journal/tag.html",
        title=tag.name,
        entries=tag.entries,
    )

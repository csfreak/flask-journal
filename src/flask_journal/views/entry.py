from flask_login import login_required

from ..forms import EntryForm
from ..models import Entry
from . import bp, werkzeugResponse
from .base import form_view, table_view


@bp.route("/entries")
@login_required
def entries() -> werkzeugResponse | str:
    return table_view(
        Entry,
        titles=[
            ("id", "#", 1),
            ("title", "Title", 5),
            ("tag_names", "Tags", 2),
            ("created_at", "Created At", 2),
            ("encrypted", "Encrypted", 1),
            ("shared", "Shared", 1),
        ],
        descending=True,
        endpoint=".entry",
    )


@bp.route("/entry", methods=["GET", "POST"])
@login_required
def entry() -> werkzeugResponse | str:
    return form_view(
        model=Entry,
        form_class=EntryForm,
        primary_fields=["Title", "Body"],
        table_view=".entries",
    )

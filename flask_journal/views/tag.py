
from flask_login import login_required

from ..forms import TagForm
from ..models import Tag
from . import bp, werkzeugResponse
from .base import form_view, table_view


@bp.route('/tags')
@login_required
def tags() -> werkzeugResponse | str:

    return table_view(Tag,
                      titles=[("id", "#", 1),
                              ("name", "Name", 3),
                              ("created_at", "Created At", 2)],
                      order_field='name',
                      endpoint=".tag")


@bp.route('/tag', methods=["GET", "POST"])
@login_required
def tag() -> werkzeugResponse | str:

    return form_view(model=Tag,
                     form_class=TagForm,
                     primary_fields=['Name'],
                     table_view='.tags')


from flask_login import login_required
from flask_security.decorators import roles_required

from ..forms import RoleForm, UserForm
from ..models import Role, User, db
from . import bp, werkzeugResponse
from .base import form_view, table_view


@bp.route('/users')
@login_required
@roles_required('admin')
def users() -> werkzeugResponse | str:

    return table_view(User,
                      titles=[("id", "#", 1),
                              ("email", "Email", 3),
                              ("created_at", "Created At", 2),
                              ("confirmed_at", "Confirmed At", 2)],
                      order_field='id',
                      endpoint=".user")


@bp.route('/user', methods=["GET", "POST"])
@login_required
def user() -> werkzeugResponse | str:

    return form_view(model=User,
                     form_class=UserForm,
                     primary_fields=['Email', 'Roles', 'Tracking', 'Settings'],
                     table_view='.users')


@bp.route('/roles')
@login_required
@roles_required('admin')
def roles() -> werkzeugResponse | str:

    return table_view(Role,
                      titles=[("id", "#", 1),
                              ("name", "Name", 3),
                              ("created_at", "Created At", 2)],
                      order_field='id',
                      endpoint=".role")


@bp.route('/role', methods=["GET", "POST"])
@login_required
@roles_required('admin')
def role() -> werkzeugResponse | str:

    return form_view(model=Role,
                     form_class=RoleForm,
                     primary_fields=['Name', 'Description'],
                     table_view='.roles')


from flask import Response, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy.sql import desc

from ..models import UserSettings
from . import bp


@bp.route('/settings')
@login_required
def settings() -> Response | str:
    settings = UserSettings.query.filter_by(user=current_user).first()

    return render_template('journal/settings.html', settings=settings)

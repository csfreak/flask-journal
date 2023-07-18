
from flask import Response, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy.sql import desc

from ..forms import UserSettingsFormSubmit
from ..models import UserSettings, db
from . import bp
from .themes import Theme


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings() -> Response | str:
    settings = UserSettings.query.filter_by(user=current_user).first()
    form = UserSettingsFormSubmit(obj=settings)

    if form.validate_on_submit():
        form.populate_obj(settings)
        db.session.add(settings)
        db.session.commit()
        flash("Settings Updated Successfully")

    return render_template('journal/settings.html', form=form, themes=list(Theme), title="Settings")

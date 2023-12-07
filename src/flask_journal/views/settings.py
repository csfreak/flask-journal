from flask import Response, flash, render_template
from flask_login import current_user, login_required
from sqlalchemy import select

from ..forms import UserSettingsForm
from ..models import UserSettings, db
from . import bp
from .themes import Theme


@bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> Response | str:
    settings = db.session.scalar(select(UserSettings).filter_by(user=current_user))

    form = UserSettingsForm(obj=settings)

    if form.validate_on_submit():
        form.populate_obj(settings)
        db.session.add(settings)
        db.session.commit()
        flash("Settings Updated Successfully")

    return render_template(
        "journal/settings.html", form=form, themes=list(Theme), title="Settings"
    )

from flask import render_template
from flask_security import current_user

from ..models import User
from . import bp, werkzeugResponse


@bp.route("/home")
def home() -> werkzeugResponse | str:
    kwargs = {"tags": None, "entry_count": None, "entries": None}
    if isinstance(current_user, User):
        if current_user.settings.home_tags:
            kwargs["tags"] = current_user.tags
            kwargs["entry_count"] = len(current_user.entries)
        if current_user.settings.home_preview:
            kwargs["entries"] = current_user.entries[-5:]
    return render_template("journal/home.html", title="Home", **kwargs)

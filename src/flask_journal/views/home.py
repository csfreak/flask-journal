from flask import render_template
from flask_security import AnonymousUser, current_user

from . import bp, werkzeugResponse


@bp.route("/home")
def home() -> werkzeugResponse | str:
    kwargs = {"tags": None, "entry_count": None, "entries": None}
    if not isinstance(current_user, AnonymousUser):
        if current_user.settings.home_tags:
            kwargs["tags"] = current_user.tags
            kwargs["entry_count"] = len(current_user.entries)
        if current_user.settings.home_preview:
            kwargs["entries"] = current_user.entries[-5:]
    return render_template("journal/home.html", **kwargs)

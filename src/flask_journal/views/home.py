from flask import render_template

from . import bp, werkzeugResponse


@bp.route("/home")
def home() -> werkzeugResponse | str:
    return render_template("journal/home.html")

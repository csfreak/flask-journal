import typing as t

from flask import Blueprint, Flask, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_login import current_user
from werkzeug import Response as werkzeugResponse

from .themes import load_theme

bp = Blueprint("journal", __name__, template_folder="templates")
bootstrap = Bootstrap5()


def init_views(app: Flask) -> None:
    from . import admin, entry, home, settings, tag  # noqa: F401

    app.register_blueprint(bp)
    bootstrap.init_app(app)


@bp.route("/")
def index() -> werkzeugResponse:
    return redirect(url_for("journal.home"), 301)


@bp.context_processor
def add_current_user() -> dict[str, t.Any]:
    return {"current_user": current_user}


@bp.app_context_processor
def add_load_theme() -> dict[str, t.Any]:
    return {"load_bootswatch_theme": load_theme}

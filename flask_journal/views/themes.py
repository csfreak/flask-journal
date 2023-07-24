from enum import StrEnum, auto

from flask import current_app
from flask_login import current_user
from markupsafe import Markup


class Theme(StrEnum):
    default = auto()
    cerulean = auto()
    cosmo = auto()
    cyborg = auto()
    darkly = auto()
    flatly = auto()
    journal = auto()
    litera = auto()
    lumen = auto()
    lux = auto()
    materia = auto()
    minty = auto()
    morph = auto()
    pulse = auto()
    quartz = auto()
    sandstone = auto()
    simplex = auto()
    sketchy = auto()
    slate = auto()
    solar = auto()
    spacelab = auto()
    superhero = auto()
    united = auto()
    vapor = auto()
    yeti = auto()
    zephyr = auto()


def load_theme() -> Markup:
    """Load Bootstrap's css resources with given version.

    .. versionadded:: 0.1.0

    :param version: The version of Bootstrap.
    """
    bs = current_app.extensions["bootstrap"]
    CDN_BASE = "https://cdn.jsdelivr.net/npm"

    bootswatch_theme = (
        current_user.settings.theme
        if current_user
        and current_user.is_authenticated
        and current_user.settings
        and current_user.settings.theme != "default"
        else current_app.config["BOOTSTRAP_BOOTSWATCH_THEME"]
    )

    version = bs.bootstrap_version
    base_path = (
        f"{CDN_BASE}/bootswatch@{version}/dist/{bootswatch_theme.lower()}"
        if bootswatch_theme
        else f"{CDN_BASE}/bootstrap@{version}/dist/css"
    )

    bootstrap_url = f"{base_path}/{bs.bootstrap_css_filename}"

    return Markup(f'<link rel="stylesheet" href="{bootstrap_url}">')

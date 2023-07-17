from enum import StrEnum, auto

from flask import Markup, current_app, url_for
from flask_login import current_user


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


def load_theme(version=None, bootstrap_sri=None):
    """Load Bootstrap's css resources with given version.

    .. versionadded:: 0.1.0

    :param version: The version of Bootstrap.
    """
    bs = current_app.extensions['bootstrap']
    CDN_BASE = 'https://cdn.jsdelivr.net/npm'

    serve_local = current_app.config['BOOTSTRAP_SERVE_LOCAL']
    bootswatch_theme = current_user.settings.theme \
        if current_user and \
        current_user.is_authenticated and \
        current_user.settings and \
        current_user.settings.theme != 'default' \
        else current_app.config['BOOTSTRAP_BOOTSWATCH_THEME']

    if version is None:
        version = bs.bootstrap_version
    bootstrap_sri = bs._get_sri('bootstrap_css', version, bootstrap_sri)

    if serve_local:
        if not bootswatch_theme:
            base_path = 'css'
        else:
            base_path = f'css/bootswatch/{bootswatch_theme.lower()}'
        boostrap_url = url_for(
            'bootstrap.static', filename=f'{base_path}/{bs.bootstrap_css_filename}')
    else:
        if not bootswatch_theme:
            base_path = f'{CDN_BASE}/bootstrap@{version}/dist/css'
        else:
            base_path = f'{CDN_BASE}/bootswatch@{version}/dist/{bootswatch_theme.lower()}'
        boostrap_url = f'{base_path}/{bs.bootstrap_css_filename}'

    if bootstrap_sri and not bootswatch_theme:
        css = f'<link rel="stylesheet" href="{boostrap_url}" integrity="{bootstrap_sri}" crossorigin="anonymous">'
    else:
        css = f'<link rel="stylesheet" href="{boostrap_url}">'
    return Markup(css)

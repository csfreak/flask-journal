
from flask import render_template

from . import bp


@bp.route('/home')
def home():
    return render_template("journal/home.html")

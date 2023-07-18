from flask import Flask, current_app, render_template
from werkzeug.exceptions import HTTPException


def handle_exception(e: HTTPException):
    current_app.logger.error(e)
    return render_template('error/generic.html', e=e), e.code


def init_errors(app: Flask) -> None:
    app.register_error_handler(HTTPException, handle_exception)

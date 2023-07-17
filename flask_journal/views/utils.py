
from flask import flash, redirect, request, url_for
from werkzeug import Response


def process_request_id() -> int | None:
    id: int | None = None
    if 'id' in request.form.keys():
        id = request.form.get('id', type=int)
    else:
        id = request.args.get('id', None, type=int)

    return id

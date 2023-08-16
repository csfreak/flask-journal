from flask.testing import FlaskClient

from flask_journal import __version__ as APP_VERSION


def test_app_info(client: FlaskClient) -> None:
    rv = client.get("/metrics")
    assert 'app_info{version="%s"}' % APP_VERSION in rv.text


def test_http_request(client: FlaskClient) -> None:
    r1 = client.get("/")
    rv = client.get("/metrics")
    assert (
        'flask_http_request_total{method="GET",status="%d"} 1.0' % r1.status_code
        in rv.text
    )

from flask.testing import FlaskClient

from flask_journal.models import User

from ...config import html_test_strings


def test_index_view(client: FlaskClient) -> None:
    rv = client.get("/")
    assert rv.status_code == 301
    assert rv.headers.get("location") == "/home"


def test_home_view_anonymous(client: FlaskClient) -> None:
    rv = client.get("/home")
    assert rv.status_code == 200
    assert "<title>Journal</title>" in rv.text
    assert html_test_strings["nav"]["login"] in rv.text
    assert html_test_strings["nav"]["register"] in rv.text
    assert html_test_strings["nav"]["roles"] not in rv.text
    assert html_test_strings["nav"]["users"] not in rv.text
    assert html_test_strings["nav"]["tags"] not in rv.text
    assert html_test_strings["nav"]["entries"] not in rv.text


def test_home_view_authenticated(
    logged_in_user_client: FlaskClient, user: User
) -> None:
    rv = logged_in_user_client.get("/home")
    assert rv.status_code == 200
    assert "<title>Journal</title>" in rv.text
    assert html_test_strings["nav"]["logout"] in rv.text
    assert html_test_strings["nav"]["settings"] in rv.text
    assert html_test_strings["nav"]["tags"] in rv.text
    assert html_test_strings["nav"]["entries"] in rv.text

    if user.has_role("admin"):
        assert html_test_strings["nav"]["roles"] in rv.text
        assert html_test_strings["nav"]["users"] in rv.text
    else:
        assert html_test_strings["nav"]["roles"] not in rv.text
        assert html_test_strings["nav"]["users"] not in rv.text

from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from flask_journal.models import Tag, User

from ...config import html_test_strings


def test_index_view(client: FlaskClient) -> None:
    rv = client.get("/")
    assert rv.status_code == 301
    assert rv.headers.get("location") == "/home"


def test_home_view_anonymous(client: FlaskClient) -> None:
    rv = client.get("/home")
    assert rv.status_code == 200
    assert html_test_strings["title"] % "Home" in rv.text
    assert html_test_strings["nav"]["login"] in rv.text
    assert html_test_strings["nav"]["register"] in rv.text
    assert html_test_strings["nav"]["roles"] not in rv.text
    assert html_test_strings["nav"]["users"] not in rv.text
    assert html_test_strings["nav"]["tags"] not in rv.text
    assert html_test_strings["nav"]["entries"] not in rv.text


def test_home_view_authenticated(
    logged_in_user_client: FlaskClient, user: User, db: SQLAlchemy
) -> None:
    db.session.add(Tag(name="test", user=user))
    db.session.commit()
    
    rv = logged_in_user_client.get("/home")
    assert rv.status_code == 200
    assert html_test_strings["title"] % "Home" in rv.text
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

    if user.settings.home_tags:
        assert html_test_strings["home"]["tag_cloud"] in rv.text
    else:
        assert html_test_strings["home"]["tag_cloud"] not in rv.text

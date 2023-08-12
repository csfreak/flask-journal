from flask.testing import FlaskClient

from flask_journal.models import User

from ...config import html_test_strings


def test_users_view(logged_in_user_client: FlaskClient, user: User) -> None:
    rv = logged_in_user_client.get("/users")
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "Users" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_user_view_admin(logged_in_user_client: FlaskClient, user: User) -> None:
    rv = logged_in_user_client.get("/user?id=1")
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "View User" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_user_view_admin_create(logged_in_user_client: FlaskClient, user: User) -> None:
    rv = logged_in_user_client.get("/user")
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "New User" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_user_view_post_create(logged_in_user_client: FlaskClient, user: User) -> None:
    rv = logged_in_user_client.post(
        "/user",
        data={
            "Email": "testuser@example.test",
            "Roles": "user",
            "Create": "Create",
        },
    )
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "View User" in rv.text
        assert html_test_strings["form"]["roles"] % "user" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_user_view_post_update_role(
    logged_in_user_client: FlaskClient, user: User
) -> None:
    rv = logged_in_user_client.post(
        "/user",
        data={
            "id": 3,
            "Email": "user3@example.test",
            "Roles": "",
            "Update": "Update",
        },
    )
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "View User" in rv.text
        assert html_test_strings["form"]["id"] % 3 in rv.text
        assert html_test_strings["form"]["roles"] % "" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_user_view_post_invalid_role(
    logged_in_user_client: FlaskClient, user: User
) -> None:
    rv = logged_in_user_client.post(
        "/user",
        data={
            "id": 3,
            "Email": "user3@example.test",
            "Roles": "user non-role",
            "Update": "Update",
        },
    )
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "View User" in rv.text
        assert html_test_strings["form"]["id"] % 3 in rv.text
        assert (
            html_test_strings["form"]["error"] % "invalid role(s): non-role" in rv.text
        )
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text

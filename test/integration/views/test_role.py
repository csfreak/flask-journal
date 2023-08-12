import pytest
from flask.testing import FlaskClient
from flask_security import datastore

from flask_journal.models import Role, User

from ...config import html_test_strings


@pytest.fixture(
    params=["admin", "manage", "user"], ids=["admin-role", "manage-role", "user-role"]
)
def role(request: pytest.FixtureRequest, userdatastore: datastore) -> Role:
    return userdatastore.find_role(request.param)


def test_roles_view(logged_in_user_client: FlaskClient, user: User) -> None:
    rv = logged_in_user_client.get("/roles")
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "Roles" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_role_view(logged_in_user_client: FlaskClient, user: User, role: Role) -> None:
    rv = logged_in_user_client.get("/role?id=%i" % role.id)
    if user.has_role("admin"):
        assert rv.status_code == 200

        assert html_test_strings["title"] % "View Role" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text


def test_role_create_view(logged_in_user_client: FlaskClient, user: User) -> None:
    rv = logged_in_user_client.get("/role")
    if user.has_role("admin"):
        assert rv.status_code == 200
        assert html_test_strings["title"] % "New Role" in rv.text
    else:
        assert rv.status_code == 403
        assert html_test_strings["title"] % "Error" in rv.text

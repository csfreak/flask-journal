import typing as t

from flask import Flask
from flask.testing import FlaskClient

from ...base import AppClientTestBase
from ...config import html_test_strings
from ...utils import authenticate


class UserViewClientTest(AppClientTestBase):
    def test_users_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/users")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Users", rv.text)

    def test_users_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user2@example.test"
        authenticate(client, email)
        rv = client.get("/users")
        self.assertStatus(rv, 403)
        self.assertIn(html_test_strings["title"] % "Error", rv.text)

    def test_user_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/user?id=1")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View User", rv.text)

    def test_user_view_admin_create(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/user")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "New User", rv.text)

    def test_user_view_post_create(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.post(
            "/user",
            data={
                "Email": "testuser@example.test",
                "Roles": "user",
                "Create": "Create",
            },
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View User", rv.text)
        self.assertIn(html_test_strings["form"]["roles"] % "user", rv.text)

    def test_user_view_post_update_role(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.post(
            "/user",
            data={
                "id": 3,
                "Email": "user3@example.test",
                "Roles": "",
                "Update": "Update",
            },
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View User", rv.text)
        self.assertIn(html_test_strings["form"]["id"] % 3, rv.text)
        self.assertIn(html_test_strings["form"]["roles"] % "", rv.text)

    def test_user_view_post_invalid_role(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.post(
            "/user",
            data={
                "id": 3,
                "Email": "user3@example.test",
                "Roles": "user non-role",
                "Update": "Update",
            },
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View User", rv.text)
        self.assertIn(html_test_strings["form"]["id"] % 3, rv.text)
        self.assertIn(
            html_test_strings["form"]["error"] % "invalid role(s): non-role", rv.text
        )


class RoleViewClientTest(AppClientTestBase):
    def test_roles_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/roles")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Roles", rv.text)

    def test_roles_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user2@example.test"
        authenticate(client, email)
        rv = client.get("/roles")
        self.assertStatus(rv, 403)
        self.assertIn(html_test_strings["title"] % "Error", rv.text)

    def test_role_view_admin(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/role?id=1")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Role", rv.text)

    def test_role_create_view_admin(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/role")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "New Role", rv.text)

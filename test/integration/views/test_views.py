import typing as t

# import pytest
from flask import Flask
from flask.testing import FlaskClient

# from flask_journal import models
from flask_journal.views.themes import Theme

from ...base import AppClientTestBase
from ...config import html_test_strings
from ...utils import authenticate

# pytest.skip("skipping legacy tests", allow_module_level=True)


class HomeViewClientTest(AppClientTestBase):
    def test_index_view(self: t.Self, app: Flask, client: FlaskClient) -> None:
        rv = client.get("/")
        self.assertStatus(rv, 301)
        self.assertLocationHeader(rv, "/home")

    def test_home_view_anon(self: t.Self, app: Flask, client: FlaskClient) -> None:
        rv = client.get("/home")
        self.assertStatus(rv, 200)
        self.assertIn("<title>Journal</title>", rv.text)
        self.assertIn(html_test_strings["nav"]["login"], rv.text)
        self.assertIn(html_test_strings["nav"]["register"], rv.text)

    def test_home_view_authed(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/home")
        self.assertStatus(rv, 200)
        self.assertIn("<title>Journal</title>", rv.text)
        self.assertIn(html_test_strings["nav"]["logout"], rv.text)
        self.assertIn(html_test_strings["nav"]["settings"], rv.text)


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


class UserSettingsViewClientTest(AppClientTestBase):
    def test_settings_view(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        rv = client.get("/settings")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Settings", rv.text)
        self.assertIn(html_test_strings["settings"]["select"], rv.text)
        self.assertIn(
            html_test_strings["settings"]["selected"] % ("default", "default"), rv.text
        )
        for theme in list(Theme):
            if theme != "default":
                self.assertIn(
                    html_test_strings["settings"]["option"] % (theme, theme), rv.text
                )

    def test_settings_post(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user1@example.test"
        authenticate(client, email)
        for theme in list(Theme):
            with self.subTest(theme=str(theme)):
                rv = client.post("/settings", data={"Theme": theme, "Update": "Update"})
                self.assertIn(html_test_strings["title"] % "Settings", rv.text)
                self.assertIn(
                    html_test_strings["settings"]["selected"] % (theme, theme), rv.text
                )
                if str(theme) == "default":
                    self.assertIn(
                        html_test_strings["settings"]["css"]["default"], rv.text
                    )
                else:
                    self.assertIn(
                        html_test_strings["settings"]["css"]["bootswatch"] % theme,
                        rv.text,
                    )

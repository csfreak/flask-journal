import typing as t

from flask import Flask
from flask.testing import FlaskClient

from flask_journal import models
from flask_journal.views.themes import Theme

from ..base import AppClientTestBase
from ..config import html_test_strings
from ..utils import authenticate


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


class TagViewClientTest(AppClientTestBase):
    def test_tags_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user2@example.test"
        authenticate(client, email)
        rv = client.get("/tags")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Tags", rv.text)
        self.assertIn("deleted_record", rv.text)

    def test_tags_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        rv = client.get("/tags")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Tags", rv.text)
        self.assertNotIn(b"deleted_record", rv.data)

    def test_tag_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user2@example.test"
        tag = models.Tag(name="tag", user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get("/tag?id=%i" % tag.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)

    def test_tag_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.get("/tag?id=%i" % tag.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)

    def test_tag_view_user_others_tag(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        tag = models.Tag(name="tag", user_id=1)
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.get("/tag?id=%i" % tag.id)
        self.assertStatus(rv, 404)
        self.assertIn(html_test_strings["title"] % "Error", rv.text)

    def test_tag_create_view_manage(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        authenticate(client, email)
        rv = client.get("/tag")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "New Tag", rv.text)

    def test_tag_create_view_user(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        rv = client.get("/tag")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "New Tag", rv.text)

    def test_tag_create_view_post_user(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        rv = client.post("/tag", data={"Name": "tag", "Create": "Create"})
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        self.assertIsInstance(
            models.Tag.query.filter_by(name="tag").first(), models.Tag
        )

    def test_tag_view_manage_delete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        tag = models.Tag(name="tag", user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        id = tag.id
        authenticate(client, email)
        rv = client.get("/tag?id=%i" % tag.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        rv = client.post("/tag?id=%i" % tag.id, data={"Delete": "Delete"})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, "/tags")
        self.assertIsNotNone(
            models.Tag.query.filter_by(id=id)
            .execution_options(include_deleted=True)
            .first()
        )

    def test_tag_view_user_delete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        id = tag.id
        authenticate(client, email)
        rv = client.get("/tag?id=%i" % tag.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        rv = client.post("/tag?id=%i" % tag.id, data={"Delete": "Delete"})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, "/tags")
        self.assertIsNotNone(
            models.Tag.query.filter_by(id=id)
            .execution_options(include_deleted=True)
            .first()
        )

    def test_tag_view_user_delete_others_tag(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post("/tag?id=%i" % tag.id, data={"Delete": "Delete"})
        self.assertStatus(rv, 404)
        self.assertIsNone(tag.deleted_at)

    def test_tag_view_user_edit(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get("/tag?id=%i" % tag.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        rv = client.post("/tag?id=%i" % tag.id, data={"Edit": "Edit"})
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Edit Tag", rv.text)

    def test_tag_view_user_edit_others_tag(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post("/tag?id=%i" % tag.id, data={"Edit": "Edit"})
        self.assertStatus(rv, 404)

    def test_tag_view_user_update(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(tag.updated_at)
        rv = client.post(
            "/tag?id=%i" % tag.id, data={"Update": "Update", "Name": "tag2"}
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        self.assertIsNotNone(tag.updated_at)
        self.assertEqual(tag.name, "tag2")

    def test_tag_view_user_update_ignore_ro(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(tag.updated_at)
        expected_create = tag.created_at
        expected_name = "tag2"
        rv = client.post(
            "/tag?id=%i" % tag.id,
            data={
                "Update": "Update",
                "Name": expected_name,
                "Created At": "abaddatevalue",
            },
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        self.assertIsNotNone(tag.updated_at)
        self.assertEqual(tag.name, expected_name)
        self.assertEqual(tag.created_at, expected_create)

    def test_tag_view_user_update_others_tag(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(tag.updated_at)
        rv = client.post(
            "/tag?id=%i" % tag.id, data={"Update": "Update", "Name": "tag2"}
        )
        self.assertStatus(rv, 404)
        self.assertIsNone(tag.updated_at)

    def test_tag_view_manage_undelete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        tag = models.Tag(name="tag", user_id=2)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        id = tag.id
        tag.delete()
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.post("/tag?id=%i" % id, data={"Undelete": "Undelete"})
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Tag", rv.text)
        self.assertIsNotNone(models.Tag.query.filter_by(id=id).first())

    def test_tag_view_manage_undelete_others_tag(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        id = tag.id
        tag.delete()
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.post("/tag?id=%i" % id, data={"Undelete": "Undelete"})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Tag.query.filter_by(id=id).first())

    def test_tag_view_user_undelete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        tag = models.Tag(name="tag", user_id=3)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        id = tag.id
        tag.delete()
        models.db.session.add(tag)
        models.db.session.commit()
        rv = client.post("/tag?id=%i" % id, data={"Undelete": "Undelete"})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Tag.query.filter_by(id=id).first())


class EntryViewClientTest(AppClientTestBase):
    def test_entries_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user2@example.test"
        authenticate(client, email)
        rv = client.get("/entries")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Entries", rv.text)
        self.assertIn("deleted_record", rv.text)

    def test_entries_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        rv = client.get("/entries")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Entries", rv.text)
        self.assertNotIn("deleted_record", rv.text)

    def test_entry_view_manage(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user2@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get("/entry?id=%i" % entry.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)

    def test_entry_view_user(self: t.Self, app: Flask, client: FlaskClient) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.get("/entry?id=%i" % entry.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)

    def test_entry_view_user_others_entry(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 1
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.get("/entry?id=%i" % entry.id)
        self.assertStatus(rv, 404)
        self.assertIn(html_test_strings["title"] % "Error", rv.text)

    def test_entry_create_view_manage(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        authenticate(client, email)
        rv = client.get("/entry")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "New Entry", rv.text)

    def test_entry_create_view_user(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        authenticate(client, email)
        rv = client.get("/entry")
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "New Entry", rv.text)

    def test_entry_create_view_post_user(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        content = "lorem ipsum"
        authenticate(client, email)
        rv = client.post(
            "/entry",
            data={"Title": "entry 1", "Body": content, "Tags": "", "Create": "Create"},
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        entry = models.Entry.query.first()
        self.assertIsInstance(entry, models.Entry)
        self.assertEqual(entry.content, content)
        self.assertNotEqual(entry.content, entry._data)

    def test_entry_create_view_post_new_tags(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        content = "lorem ipsum"
        authenticate(client, email)
        rv = client.post(
            "/entry",
            data={
                "Title": "entry 1",
                "Body": content,
                "Tags": "testtag",
                "Create": "Create",
            },
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        entry = models.Entry.query.first()
        self.assertIsInstance(entry, models.Entry)
        self.assertEqual(entry.content, content)
        self.assertNotEqual(entry.content, entry._data)
        tag = models.Tag.query.filter_by(name="testtag").first()
        self.assertIsInstance(tag, models.Tag)

    def test_entry_create_view_post_existing_tags(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        content = "lorem ipsum"
        user = models.User.query.filter_by(email=email).first()
        tag = models.Tag(name="testtag", user=user)
        models.db.session.add(tag)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post(
            "/entry",
            data={
                "Title": "entry 1",
                "Body": content,
                "Tags": "testtag",
                "Create": "Create",
            },
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        entry = models.Entry.query.first()
        self.assertIsInstance(entry, models.Entry)
        self.assertEqual(entry.content, content)
        self.assertNotEqual(entry.content, entry._data)
        self.assertIs(entry.tags[0], tag)

    def test_entry_view_manage_delete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        id = entry.id
        authenticate(client, email)
        rv = client.get("/entry?id=%i" % entry.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        rv = client.post("/entry?id=%i" % entry.id, data={"Delete": "Delete"})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, "/entries")
        self.assertIsNotNone(
            models.Entry.query.filter_by(id=id)
            .execution_options(include_deleted=True)
            .first()
        )

    def test_entry_view_user_delete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        id = entry.id
        authenticate(client, email)
        rv = client.get("/entry?id=%i" % entry.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        rv = client.post("/entry?id=%i" % entry.id, data={"Delete": "Delete"})
        self.assertStatus(rv, 302)
        self.assertLocationHeader(rv, "/entries")
        self.assertIsNotNone(
            models.Entry.query.filter_by(id=id)
            .execution_options(include_deleted=True)
            .first()
        )

    def test_entry_view_user_delete_others_entry(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post("/entry?id=%i" % entry.id, data={"Delete": "Delete"})
        self.assertStatus(rv, 404)
        self.assertIsNone(entry.deleted_at)

    def test_entry_view_user_edit(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.get("/entry?id=%i" % entry.id)
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        rv = client.post("/entry?id=%i" % entry.id, data={"Edit": "Edit"})
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "Edit Entry", rv.text)

    def test_entry_view_user_edit_others_entry(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        rv = client.post("/entry?id=%i" % entry.id, data={"Edit": "Edit"})
        self.assertStatus(rv, 404)

    def test_entry_view_user_update(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(entry.updated_at)
        rv = client.post(
            "/entry?id=%i" % entry.id, data={"Update": "Update", "Title": "entry2"}
        )
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)

        self.assertIsNotNone(entry.updated_at)

    def test_entry_view_user_update_others_entry(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        self.assertIsNone(entry.updated_at)
        rv = client.post(
            "/entry?id=%i" % entry.id, data={"Update": "Update", "Name": "entry2"}
        )
        self.assertStatus(rv, 404)
        self.assertIsNone(entry.updated_at)

    def test_entry_view_manage_undelete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 2
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        id = entry.id
        entry.delete()
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.post("/entry?id=%i" % id, data={"Undelete": "Undelete"})
        self.assertStatus(rv, 200)
        self.assertIn(html_test_strings["title"] % "View Entry", rv.text)
        self.assertIsNotNone(models.Entry.query.filter_by(id=id).first())

    def test_entry_view_manage_undelete_others_entry(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user2@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        id = entry.id
        entry.delete()
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.post("/entry?id=%i" % id, data={"Undelete": "Undelete"})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Entry.query.filter_by(id=id).first())

    def test_entry_view_user_undelete(
        self: t.Self, app: Flask, client: FlaskClient
    ) -> None:
        email = "user3@example.test"
        entry = models.Entry()
        entry.title = "entry"
        entry.content = "lorem ipsum"
        entry.user_id = 3
        models.db.session.add(entry)
        models.db.session.commit()
        authenticate(client, email)
        id = entry.id
        entry.delete()
        models.db.session.add(entry)
        models.db.session.commit()
        rv = client.post("/entry?id=%i" % id, data={"Undelete": "Undelete"})
        self.assertStatus(rv, 404)
        self.assertIsNone(models.Entry.query.filter_by(id=id).first())


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

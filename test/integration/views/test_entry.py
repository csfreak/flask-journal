# import typing as t

import pytest

# from flask import Flask
from flask.testing import FlaskClient

from ...config import html_test_strings

# from flask_journal import models
# from flask_journal.views.themes import Theme


@pytest.mark.parametrize(
    "logged_in_user_client",
    ["user2@example.test", "user3@example.test"],
    indirect=True,
    ids=["manage", "user"],
)
def test_entries_view(logged_in_user_client: FlaskClient) -> None:
    rv = logged_in_user_client.get("/entries")
    assert rv.status_code == 200
    assert html_test_strings["title"] % "Entries" in rv.text
    # self.assertNotIn("deleted_record", rv.text)


# def test_entry_view_manage(client: FlaskClient) -> None:
#     email = "user2@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 2
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     rv = client.get("/entry?id=%i" % entry.id)
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text

# def test_entry_view_user(client: FlaskClient) -> None:
#     email = "user3@example.test"
#     authenticate(client, email)
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 3
#     models.db.session.add(entry)
#     models.db.session.commit()
#     rv = client.get("/entry?id=%i" % entry.id)
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text

# def test_entry_view_user_others_entry(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     authenticate(client, email)
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 1
#     models.db.session.add(entry)
#     models.db.session.commit()
#     rv = client.get("/entry?id=%i" % entry.id)
#     self.assertStatus(rv, 404)
#     assert html_test_strings["title"] % "Error" in rv.text

# def test_entry_create_view_manage(
#     client: FlaskClient
# ) -> None:
#     email = "user2@example.test"
#     authenticate(client, email)
#     rv = client.get("/entry")
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "New Entry" in rv.text

# def test_entry_create_view_user(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     authenticate(client, email)
#     rv = client.get("/entry")
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "New Entry" in rv.text

# def test_entry_create_view_post_user(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     content = "lorem ipsum"
#     authenticate(client, email)
#     rv = client.post(
#         "/entry",
#         data={"Title": "entry 1", "Body": content, "Tags": "", "Create": "Create"},
#     )
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     entry = models.Entry.query.first()
#     self.assertIsInstance(entry, models.Entry)
#     self.assertEqual(entry.content, content)
#     self.assertNotEqual(entry.content, entry._data)

# def test_entry_create_view_post_new_tags(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     content = "lorem ipsum"
#     authenticate(client, email)
#     rv = client.post(
#         "/entry",
#         data={
#             "Title": "entry 1",
#             "Body": content,
#             "Tags": "testtag",
#             "Create": "Create",
#         },
#     )
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     entry = models.Entry.query.first()
#     self.assertIsInstance(entry, models.Entry)
#     self.assertEqual(entry.content, content)
#     self.assertNotEqual(entry.content, entry._data)
#     tag = models.Tag.query.filter_by(name="testtag").first()
#     self.assertIsInstance(tag, models.Tag)

# def test_entry_create_view_post_existing_tags(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     content = "lorem ipsum"
#     user = models.User.query.filter_by(email=email).first()
#     tag = models.Tag(name="testtag", user=user)
#     models.db.session.add(tag)
#     models.db.session.commit()
#     authenticate(client, email)
#     rv = client.post(
#         "/entry",
#         data={
#             "Title": "entry 1",
#             "Body": content,
#             "Tags": "testtag",
#             "Create": "Create",
#         },
#     )
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     entry = models.Entry.query.first()
#     self.assertIsInstance(entry, models.Entry)
#     self.assertEqual(entry.content, content)
#     self.assertNotEqual(entry.content, entry._data)
#     self.assertIs(entry.tags[0], tag)

# def test_entry_view_manage_delete(
#     client: FlaskClient
# ) -> None:
#     email = "user2@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 2
#     models.db.session.add(entry)
#     models.db.session.commit()
#     id = entry.id
#     authenticate(client, email)
#     rv = client.get("/entry?id=%i" % entry.id)
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     rv = client.post("/entry?id=%i" % entry.id, data={"Delete": "Delete"})
#     assert rv.status_code == 302
#     self.assertLocationHeader(rv, "/entries")
#     self.assertIsNotNone(
#         models.Entry.query.filter_by(id=id)
#         .execution_options(include_deleted=True)
#         .first()
#     )

# def test_entry_view_user_delete(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 3
#     models.db.session.add(entry)
#     models.db.session.commit()
#     id = entry.id
#     authenticate(client, email)
#     rv = client.get("/entry?id=%i" % entry.id)
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     rv = client.post("/entry?id=%i" % entry.id, data={"Delete": "Delete"})
#     assert rv.status_code == 302
#     self.assertLocationHeader(rv, "/entries")
#     self.assertIsNotNone(
#         models.Entry.query.filter_by(id=id)
#         .execution_options(include_deleted=True)
#         .first()
#     )

# def test_entry_view_user_delete_others_entry(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 2
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     rv = client.post("/entry?id=%i" % entry.id, data={"Delete": "Delete"})
#     self.assertStatus(rv, 404)
#     self.assertIsNone(entry.deleted_at)

# def test_entry_view_user_edit(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 3
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     rv = client.get("/entry?id=%i" % entry.id)
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     rv = client.post("/entry?id=%i" % entry.id, data={"Edit": "Edit"})
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "Edit Entry" in rv.text

# def test_entry_view_user_edit_others_entry(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 2
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     rv = client.post("/entry?id=%i" % entry.id, data={"Edit": "Edit"})
#     self.assertStatus(rv, 404)

# def test_entry_view_user_update(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 3
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     self.assertIsNone(entry.updated_at)
#     rv = client.post(
#         "/entry?id=%i" % entry.id, data={"Update": "Update", "Title": "entry2"}
#     )
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text

#     self.assertIsNotNone(entry.updated_at)

# def test_entry_view_user_update_others_entry(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 2
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     self.assertIsNone(entry.updated_at)
#     rv = client.post(
#         "/entry?id=%i" % entry.id, data={"Update": "Update", "Name": "entry2"}
#     )
#     self.assertStatus(rv, 404)
#     self.assertIsNone(entry.updated_at)

# def test_entry_view_manage_undelete(
#     client: FlaskClient
# ) -> None:
#     email = "user2@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 2
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     id = entry.id
#     entry.delete()
#     models.db.session.add(entry)
#     models.db.session.commit()
#     rv = client.post("/entry?id=%i" % id, data={"Undelete": "Undelete"})
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "View Entry" in rv.text
#     self.assertIsNotNone(models.Entry.query.filter_by(id=id).first())

# def test_entry_view_manage_undelete_others_entry(
#     client: FlaskClient
# ) -> None:
#     email = "user2@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 3
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     id = entry.id
#     entry.delete()
#     models.db.session.add(entry)
#     models.db.session.commit()
#     rv = client.post("/entry?id=%i" % id, data={"Undelete": "Undelete"})
#     self.assertStatus(rv, 404)
#     self.assertIsNone(models.Entry.query.filter_by(id=id).first())

# def test_entry_view_user_undelete(
#     client: FlaskClient
# ) -> None:
#     email = "user3@example.test"
#     entry = models.Entry()
#     entry.title = "entry"
#     entry.content = "lorem ipsum"
#     entry.user_id = 3
#     models.db.session.add(entry)
#     models.db.session.commit()
#     authenticate(client, email)
#     id = entry.id
#     entry.delete()
#     models.db.session.add(entry)
#     models.db.session.commit()
#     rv = client.post("/entry?id=%i" % id, data={"Undelete": "Undelete"})
#     self.assertStatus(rv, 404)
#     self.assertIsNone(models.Entry.query.filter_by(id=id).first())


# class UserSettingsViewClientTest(AppClientTestBase):
# def test_settings_view(client: FlaskClient) -> None:
#     email = "user1@example.test"
#     authenticate(client, email)
#     rv = client.get("/settings")
#     assert rv.status_code == 200
#     assert html_test_strings["title"] % "Settings" in rv.text
#     assert html_test_strings["settings"]["select"] in rv.text
#     self.assertIn(
#         html_test_strings["settings"]["selected"] % ("default", "default"), rv.text
#     )
#     for theme in list(Theme):
#         if theme != "default":
#             self.assertIn(
#                 html_test_strings["settings"]["option"] % (theme, theme), rv.text
#             )

# def test_settings_post(client: FlaskClient) -> None:
#     email = "user1@example.test"
#     authenticate(client, email)
#     for theme in list(Theme):
#         with self.subTest(theme=str(theme)):
#             rv = client.post("/settings", data={"Theme": theme, "Update": "Update"})
#             assert html_test_strings["title"] % "Settings" in rv.text
#             self.assertIn(
#                 html_test_strings["settings"]["selected"] % (theme, theme), rv.text
#             )
#             if str(theme) == "default":
#                 self.assertIn(
#                     html_test_strings["settings"]["css"]["default"], rv.text
#                 )
#             else:
#                 self.assertIn(
#                     html_test_strings["settings"]["css"]["bootswatch"] % theme,
#                     rv.text,
#                 )

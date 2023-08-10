# import typing as t

import pytest

# from flask import Flask
from flask.testing import FlaskClient

from flask_journal import models

from ...config import html_test_strings

# from flask_journal.views.themes import Theme


@pytest.fixture
def entries(request: pytest.FixtureRequest, user: models.User) -> list[models.Entry]:
    entries: list[models.Entry] = []
    for i in range(request.param):
        entry = models.Entry()
        entry.title = f"TestEntry {i}"
        entry.content = "lorem ipsum"
        entry.user = user
        if i % 2:
            entry.delete()
        models.db.session.add(entry)
        entries.append(entry)
    models.db.session.commit()
    return entries


@pytest.mark.parametrize(
    ("user", "entries"),
    [
        ("user2@example.test", 4),
        ("user3@example.test", 4),
    ],
    indirect=True,
    ids=["manage", "user"],
)
def test_entries_view(
    logged_in_user_client: FlaskClient, user: models.User, entries: list[models.Entry]
) -> None:
    rv = logged_in_user_client.get("/entries")
    entries = (
        models.Entry.query.filter_by(user=user)
        .execution_options(include_deleted=True)
        .all()
    )
    assert rv.status_code == 200
    assert html_test_strings["title"] % "Entries" in rv.text
    if user.has_role("manage"):
        assert "deleted_record" in rv.text
        for entry in entries:
            assert entry.title in rv.text
    else:
        for entry in entries:
            if entry.active:
                assert entry.title in rv.text
            else:
                assert entry.title not in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize("entries", [1], ids=["single"], indirect=True)
def test_entry_view(
    logged_in_user_client: FlaskClient, entries: list[models.Entry]
) -> None:
    rv = logged_in_user_client.get("/entry?id=%i" % entries[0].id)
    assert rv.status_code == 200
    assert html_test_strings["title"] % "View Entry" in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
def test_entry_view_others(
    logged_in_user_client: FlaskClient, user: models.User
) -> None:
    entry = models.Entry(title="Entry 1", content="lorem ipsum", user_id=user.id + 1)
    models.db.session.add(entry)
    models.db.session.commit()

    rv = logged_in_user_client.get("/entry?id=%i" % entry.id)
    assert rv.status_code == 404
    assert html_test_strings["title"] % "Error" in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
def test_entry_create_view(
    logged_in_user_client: FlaskClient, user: models.User
) -> None:
    rv = logged_in_user_client.get("/entry")
    assert rv.status_code == 200
    assert html_test_strings["title"] % "New Entry" in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize(
    "tags",
    ["", "existingtag", "newtag", "newtag existingtag"],
    ids=["no-tag", "existing-tag", "new-tag", "multiple-tags"],
)
def test_entry_create_post(
    logged_in_user_client: FlaskClient, user: models.User, tags: str
) -> None:
    expected_title = "Entry 1"
    expected_body = "lorem ipsum"
    expected_tags = [tag for tag in tags.split(" ") if tag]
    for tag in expected_tags:
        if "existing" in tags:
            models.db.session.add(models.Tag(user=user, name=tag))
    models.db.session.commit()

    rv = logged_in_user_client.post(
        "/entry",
        data={
            "Title": expected_title,
            "Body": expected_body,
            "Tags": tags,
            "Create": "Create",
        },
    )
    assert rv.status_code == 200
    assert html_test_strings["title"] % "View Entry" in rv.text
    entry = models.Entry.query.first()
    assert isinstance(entry, models.Entry)
    assert entry.content == expected_body
    assert entry.content != entry._data
    for tag in expected_tags:
        t = models.Tag.query.filter_by(name=tag, user=user).first()
        assert isinstance(t, models.Tag)
        assert t in entry.tags

    for tag in entry.tags:
        assert tag.name in expected_tags


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

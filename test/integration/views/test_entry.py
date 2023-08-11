import pytest
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from flask_journal import models

from ...config import html_test_strings


@pytest.fixture
def entries(
    request: pytest.FixtureRequest, user: models.User, db: SQLAlchemy
) -> list[models.Entry]:
    entries: list[models.Entry] = []
    for i in range(request.param):
        entry = models.Entry()
        entry.title = f"TestEntry {i}"
        entry.content = "lorem ipsum"
        entry.user = user
        if i % 2:
            entry.delete()
        db.session.add(entry)
        entries.append(entry)
    db.session.commit()
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
    logged_in_user_client: FlaskClient, user: models.User, db: SQLAlchemy
) -> None:
    entry = models.Entry(title="Entry 1", content="lorem ipsum", user_id=user.id + 1)
    db.session.add(entry)
    db.session.commit()

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
    logged_in_user_client: FlaskClient, user: models.User, tags: str, db: SQLAlchemy
) -> None:
    expected_title = "Entry 1"
    expected_body = "lorem ipsum"
    expected_tags = [tag for tag in tags.split(" ") if tag]
    for tag in expected_tags:
        if "existing" in tags:
            db.session.add(models.Tag(user=user, name=tag))
    db.session.commit()

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


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize("button", ["Edit", "Update", "Delete", "Undelete"])
def test_entry_view_post_others(
    logged_in_user_client: FlaskClient, user: models.User, button: str, db: SQLAlchemy
) -> None:
    entry = models.Entry(title="Entry 1", content="lorem ipsum", user_id=user.id + 1)
    db.session.add(entry)
    db.session.commit()
    id = entry.id
    post_data = {button: button}
    match button:
        case "Undelete":
            entry.delete()
            db.session.add(entry)
            db.session.commit()
        case "Update":
            post_data["Title"] = "updatedtitle"

    rv = logged_in_user_client.post("/entry?id=%i" % id, data=post_data)
    assert rv.status_code == 404
    assert html_test_strings["title"] % "Error" in rv.text
    match button:
        case "Delete":
            db.session.expire(entry)
            assert entry.active
        case "Undelete":
            entry = (
                models.Entry.query.filter_by(id=id)
                .execution_options(include_deleted=True)
                .first()
            )
            assert not entry.active
        case "Update":
            db.session.expire(entry)
            assert entry.title != "updatedtitle"
            assert entry.updated_at is None


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize("button", ["Edit", "Update", "Delete", "Undelete"])
def test_entry_view_post(
    logged_in_user_client: FlaskClient, user: models.User, button: str, db: SQLAlchemy
) -> None:
    entry = models.Entry(title="Entry 1", content="lorem ipsum", user=user)
    db.session.add(entry)
    db.session.commit()
    id = entry.id
    post_data = {button: button}
    match button:
        case "Undelete":
            entry.delete()
            db.session.add(entry)
            db.session.commit()
        case "Update":
            post_data["Title"] = "updatedtitle"
    db.session.expire(entry)

    rv = logged_in_user_client.post("/entry?id=%i" % id, data=post_data)

    match button:
        case "Delete":
            entry = (
                models.Entry.query.filter_by(id=id)
                .execution_options(include_deleted=True)
                .first()
            )
            assert not entry.active
            assert rv.status_code == 302
            assert rv.headers.get("location") == "/entries"
        case "Undelete":
            if user.has_role("manage"):
                assert rv.status_code == 200
                assert html_test_strings["title"] % "View Entry" in rv.text
                assert entry.active
            else:
                assert rv.status_code == 404
                assert html_test_strings["title"] % "Error" in rv.text
                entry = (
                    models.Entry.query.filter_by(id=id)
                    .execution_options(include_deleted=True)
                    .first()
                )
                assert not entry.active
        case "Update":
            assert entry.title == "updatedtitle"
            assert entry.updated_at is not None
            assert rv.status_code == 200
            assert html_test_strings["title"] % "View Entry" in rv.text
        case "Edit":
            assert rv.status_code == 200
            assert html_test_strings["title"] % "Edit Entry" in rv.text

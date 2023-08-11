import pytest
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from flask_journal import models

from ...config import html_test_strings


@pytest.fixture
def tags(
    request: pytest.FixtureRequest, user: models.User, db: SQLAlchemy
) -> list[models.Tag]:
    tags: list[models.Tag] = []
    for i in range(request.param):
        tag = models.Tag()
        tag.name = f"TestTag {i}"
        tag.user = user
        if i % 2:
            tag.delete()
        db.session.add(tag)
        tags.append(tag)
    db.session.commit()
    return tags


@pytest.mark.parametrize(
    ("user", "tags"),
    [
        ("user2@example.test", 4),
        ("user3@example.test", 4),
    ],
    indirect=True,
    ids=["manage", "user"],
)
def test_tags_view(
    logged_in_user_client: FlaskClient, user: models.User, tags: list[models.Tag]
) -> None:
    rv = logged_in_user_client.get("/tags")
    tags = (
        models.Tag.query.filter_by(user=user)
        .execution_options(include_deleted=True)
        .all()
    )
    assert rv.status_code == 200
    assert html_test_strings["title"] % "Tags" in rv.text
    if user.has_role("manage"):
        assert "deleted_record" in rv.text
        for tag in tags:
            assert tag.name in rv.text
    else:
        for tag in tags:
            if tag.active:
                assert tag.name in rv.text
            else:
                assert tag.name not in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize("tags", [1], ids=["single"], indirect=True)
def test_tag_view(logged_in_user_client: FlaskClient, tags: list[models.Tag]) -> None:
    rv = logged_in_user_client.get("/tag?id=%i" % tags[0].id)
    assert rv.status_code == 200
    assert html_test_strings["title"] % "View Tag" in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
def test_tag_view_others(
    logged_in_user_client: FlaskClient, user: models.User, db: SQLAlchemy
) -> None:
    tag = models.Tag(name="Tag 1", user_id=user.id + 1)
    db.session.add(tag)
    db.session.commit()

    rv = logged_in_user_client.get("/tag?id=%i" % tag.id)
    assert rv.status_code == 404
    assert html_test_strings["title"] % "Error" in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
def test_tag_create_view(logged_in_user_client: FlaskClient, user: models.User) -> None:
    rv = logged_in_user_client.get("/tag")
    assert rv.status_code == 200
    assert html_test_strings["title"] % "New Tag" in rv.text


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
def test_tag_create_post(logged_in_user_client: FlaskClient, user: models.User) -> None:
    expected_name = "Tag 1"

    rv = logged_in_user_client.post(
        "/tag",
        data={
            "Name": expected_name,
            "Create": "Create",
        },
    )
    assert rv.status_code == 200
    assert html_test_strings["title"] % "View Tag" in rv.text
    tag = models.Tag.query.first()
    assert isinstance(tag, models.Tag)
    assert tag.name == expected_name


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize("button", ["Edit", "Update", "Delete", "Undelete"])
def test_tag_view_post_others(
    logged_in_user_client: FlaskClient, user: models.User, button: str, db: SQLAlchemy
) -> None:
    tag = models.Tag(name="Tag 1", user_id=user.id + 1)
    db.session.add(tag)
    db.session.commit()
    id = tag.id
    post_data = {button: button}
    match button:
        case "Undelete":
            tag.delete()
            db.session.add(tag)
            db.session.commit()
        case "Update":
            post_data["Name"] = "updatedname"

    rv = logged_in_user_client.post("/tag?id=%i" % id, data=post_data)
    assert rv.status_code == 404
    assert html_test_strings["title"] % "Error" in rv.text
    match button:
        case "Delete":
            db.session.expire(tag)
            assert tag.active
        case "Undelete":
            tag = (
                models.Tag.query.filter_by(id=id)
                .execution_options(include_deleted=True)
                .first()
            )
            assert not tag.active
        case "Update":
            db.session.expire(tag)
            assert tag.name != "updatedname"
            assert tag.updated_at is None


@pytest.mark.parametrize(
    "user",
    ["user1@example.test", "user2@example.test", "user3@example.test"],
    ids=["admin", "manage", "user"],
    indirect=True,
)
@pytest.mark.parametrize("button", ["Edit", "Update", "Delete", "Undelete"])
def test_tag_view_post(
    logged_in_user_client: FlaskClient, user: models.User, button: str, db: SQLAlchemy
) -> None:
    tag = models.Tag(name="Tag 1", user=user)
    db.session.add(tag)
    db.session.commit()
    id = tag.id
    post_data = {button: button}
    match button:
        case "Undelete":
            tag.delete()
            db.session.add(tag)
            db.session.commit()
        case "Update":
            post_data["Name"] = "updatedname"
    db.session.expire(tag)

    rv = logged_in_user_client.post("/tag?id=%i" % id, data=post_data)

    match button:
        case "Delete":
            tag = (
                models.Tag.query.filter_by(id=id)
                .execution_options(include_deleted=True)
                .first()
            )
            assert not tag.active
            assert rv.status_code == 302
            assert rv.headers.get("location") == "/tags"
        case "Undelete":
            if user.has_role("manage"):
                assert rv.status_code == 200
                assert html_test_strings["title"] % "View Tag" in rv.text
                assert tag.active
            else:
                assert rv.status_code == 404
                assert html_test_strings["title"] % "Error" in rv.text
                tag = (
                    models.Tag.query.filter_by(id=id)
                    .execution_options(include_deleted=True)
                    .first()
                )
                assert not tag.active
        case "Update":
            assert tag.name == "updatedname"
            assert tag.updated_at is not None
            assert rv.status_code == 200
            assert html_test_strings["title"] % "View Tag" in rv.text
        case "Edit":
            assert rv.status_code == 200
            assert html_test_strings["title"] % "Edit Tag" in rv.text

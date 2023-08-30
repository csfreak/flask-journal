import pytest

from flask_journal.models import User, db
from flask_journal.views import home as home_view


@pytest.mark.parametrize(
    "user",
    ["user3@example.test"],
    ids=["base-user"],
    indirect=True,
)
@pytest.mark.parametrize(
    "home_tags",
    [None, True, False],
    ids=["default_tags", "true_tags", "false_tags"],
)
@pytest.mark.parametrize(
    "home_preview",
    [None, True, False],
    ids=["default_preview", "true_preview", "false_preview"],
)
@pytest.mark.usefixtures("logged_in_user_context")
def test_home_auth(
    user: User,
    home_tags: bool | None,
    home_preview: bool | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if home_tags is not None:
        user.settings.home_tags = home_tags
    else:
        home_tags = True
    if home_preview is not None:
        user.settings.home_preview = home_preview
    else:
        home_preview = True
    db.session.add(user)
    db.session.commit()

    monkeypatch.setattr(home_view, "render_template", lambda t, **kwargs: kwargs)

    r = home_view.home()
    if home_tags:
        assert r["tags"] is not None
        assert r["entry_count"] is not None
    else:
        assert r["tags"] is None
        assert r["entry_count"] is None

    if home_preview:
        assert r["entries"] is not None
    else:
        assert r["entries"] is None

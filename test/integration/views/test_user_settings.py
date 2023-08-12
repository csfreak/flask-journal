import pytest
from flask.testing import FlaskClient

from flask_journal.views.themes import Theme

from ...config import html_test_strings


def test_setttings_view(logged_in_user_client: FlaskClient) -> None:
    rv = logged_in_user_client.get("/settings")
    assert rv.status_code == 200
    assert html_test_strings["title"] % "Settings" in rv.text
    assert html_test_strings["settings"]["select"] in rv.text
    assert html_test_strings["settings"]["selected"] % ("default" in "default", rv.text)
    for theme in list(Theme):
        if theme != "default":
            assert html_test_strings["settings"]["option"] % (theme in theme, rv.text)


@pytest.mark.parametrize(
    "theme",
    list(Theme),
)
def test_settings_update_theme(
    logged_in_user_client: FlaskClient, theme: Theme
) -> None:
    rv = logged_in_user_client.post(
        "/settings", data={"Theme": str(theme), "Update": "Update"}
    )
    assert html_test_strings["title"] % "Settings" in rv.text
    assert html_test_strings["settings"]["selected"] % (theme, theme) in rv.text

    if str(theme) == "default":
        assert html_test_strings["settings"]["css"]["default"] in rv.text
    else:
        assert (
            html_test_strings["settings"]["css"]["bootswatch"] % str(theme) in rv.text
        )

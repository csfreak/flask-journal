import pathlib
import sys

import pytest
from gunicorn.app.wsgiapp import run


def test_config_imports(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    argv = [
        "gunicorn",
        "--check-config",
        "--config",
        "scripts/gunicorn.config.py",
        "flask_journal.app:create_app()",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", tmp_path.as_posix())
    monkeypatch.setenv("JOURNAL_SQLALCHEMY_DATABASE_URI", "sqlite://")
    with pytest.raises(SystemExit) as excinfo:
        run()

    assert excinfo.value.args[0] == 0

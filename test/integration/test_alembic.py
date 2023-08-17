import pytest
from alembic import command
from alembic.config import Config


@pytest.mark.parametrize("url", ["mysql+pymysql://localhost"], ids=["mysql"])
def test_alembic_sql(url: str, capsys: pytest.CaptureFixture) -> None:
    alembic_cfg = Config("migrations/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(alembic_cfg, "head", True)
    out, err = capsys.readouterr()
    assert out.startswith("CREATE TABLE alembic_version")

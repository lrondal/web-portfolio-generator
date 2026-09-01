"""The Alembic baseline builds the whole schema from an empty database."""

from pathlib import Path

import sqlalchemy as sa
from alembic import command
from alembic.config import Config

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_baseline_migration_builds_full_schema_from_empty(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "migrated.db"
    url = f"sqlite:///{db_path}"
    monkeypatch.setenv("DATABASE_URL", url)

    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))

    command.upgrade(config, "head")

    inspector = sa.inspect(sa.create_engine(url))
    tables = set(inspector.get_table_names())
    assert {"account", "portfolio", "project"} <= tables
    assert "user" not in tables
    assert {c["name"] for c in inspector.get_columns("account")} == {
        "account_id",
        "email",
        "password_hash",
        "display_name",
        "age",
        "contact_email",
        "github",
        "phone",
    }

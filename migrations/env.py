"""Alembic environment.

The URL comes from ``DATABASE_URL`` (the same source as the app), so a deploy
runs its migrations against the same Postgres the app will use. Importing
``main`` registers the SQLModel tables on the shared metadata used for
autogenerate.
"""

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel

import main  # imported for its table definitions and DB-URL resolution

config = context.config
config.set_main_option("sqlalchemy.url", main.resolve_database_url())

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

---
status: accepted
---

# Managed Postgres for persistence, replacing SQLite-on-Render

Data moves from a local SQLite file to a managed Postgres instance (Neon or
Render Postgres). Render rebuilds the app's filesystem on every deploy and on
idle restarts, so the SQLite file — and every account created since the last
restart — is silently lost. A managed database persists independently of the
app process.

## Considered options

- **Render persistent disk + SQLite.** Cheapest, smallest change; rejected for
  single-instance limits and DIY backups.
- **SQLite + Litestream replication.** Durable; rejected as an extra process to
  run and reason about.

## Consequences

- Adds a network dependency and a connection-string secret to manage.
- Needs a migration tool (e.g. Alembic) — the schema is no longer recreated from
  scratch on each boot.
- SQLModel already sits on SQLAlchemy, so the application code change is small.

# web-portfolio-generator

FastAPI + SQLModel app that stores users and their projects (SQLite) and
renders portfolio / CV pages from Jinja2 templates.

## Git workflow

Agents making code edits MUST NOT commit to `main`. Create a branch first
(e.g. `agent/<short-description>`), commit there, and open a pull request.
Never push to `main`, force-push, or merge.

## Agent skills

### Issue tracker

Issues live as GitHub issues in `lrondal/web-portfolio-generator`; use the `gh` CLI.
See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

# web-portfolio-generator

FastAPI + SQLModel app that stores users and their projects (SQLite) and
renders portfolio / CV pages from Jinja2 templates.

## Active epic: self-serve account model

All ticket work for this epic branches from and targets
`epic/self-serve-account-model`, **not** `main`.

- Start:  `git switch -c ticket/<n>-<slug> origin/epic/self-serve-account-model`
- PR:     `gh pr create --base epic/self-serve-account-model --head ticket/<n>-<slug>`
- Verify: `gh pr view <n> --json baseRefName` must report `epic/self-serve-account-model`.

Remove this section once `epic/self-serve-account-model` is merged into `main`.

## Agent skills

### Issue tracker

Issues live as GitHub issues in `lrondal/web-portfolio-generator`; use the `gh` CLI.
See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`,
`ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

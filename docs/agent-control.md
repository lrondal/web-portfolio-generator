# Agent control

**Instruction — `.claude/skills/domain-vocabulary-check/`.** Fires when a
change renames a model field, route, template, or test to match CONTEXT.md's
domain vocabulary, or right before committing a diff that touches `main.py`,
`template/`, or `migrations/`: it greps the diff for any `_Avoid_` term
(CONTEXT.md's banned synonyms — "tags" for "skill list", "CV" for
"Portfolio") and, for each hit, checks whether a specific ADR actually names
that exact usage rather than just sitting near the concept. It should *not*
fire on a change that touches those files but names no glossary term — e.g.
adding a `/health` liveness endpoint edits `main.py` but has no domain
concept in play; a fresh test confirmed the agent checked CONTEXT.md/ADRs,
correctly found nothing relevant, and left the skill alone. See
`docs/agent-control-evidence.md` for the fired/didn't-fire transcripts and
what step 3b's prune changed.

**Enforcement — `.claude/hooks/block_main_git_ops.py`.** Registered as a
`PreToolUse` hook on every `Bash` call, it blocks (exit 2, not a warning)
`git commit` while on `main`, any `git push` targeting `main`, any
force-push, and any `git merge`. Instruction alone wasn't enough: CLAUDE.md
already said, in plain English, that agents must not commit to `main`, and
the commit history from before that rule existed is almost all direct
commits to `main` anyway. The failure mode isn't carelessness — it's
non-determinism. An identical prompt, context, and model can still produce a
different tool call on a given run, so an instruction gets followed roughly
nine times in ten, and the tenth is exactly the expensive one (a commit that
already happened, repeatedly, before this hook did). The hook doesn't ask
the model to comply; it removes the choice.

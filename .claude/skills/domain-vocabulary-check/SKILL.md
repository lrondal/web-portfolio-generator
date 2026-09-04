---
name: domain-vocabulary-check
description: Checks a change against CONTEXT.md's domain glossary before it's finalized -- catches an _Avoid_ term (a banned synonym like "tags" for "skill list", or "CV" for "Portfolio") creeping back into code, comments, file names, or templates, and confirms any exception is backed by an ADR. Use when renaming a model field, route, template, or test to match domain vocabulary; when writing a comment or docstring next to such a rename; or right before committing a diff that touches main.py, template/, or migrations/.
---

# Domain vocabulary check

CONTEXT.md's glossary gives each domain concept one canonical name and
lists the synonyms to avoid for it (`_Avoid_:`). This skill exists because
a rename fixes the obvious spot (a field, a variable) and then reintroduces
the same banned word one line away, in a comment or a file name nobody
double-checked.

## Do this, in order

1. Read CONTEXT.md's glossary. For each concept, note its `_Avoid_:` terms.
2. Get the diff you're about to commit (`git diff`, staged or working tree).
   Search it for every `_Avoid_` term as a whole word -- in identifiers,
   comments, strings, file names, and template `name=`/`src=` attributes.
   Case-insensitive; comments and docstrings count.
3. For each hit, decide:
   - **No ADR covers it** -> replace it with the canonical term.
   - **An ADR in `docs/adr/` explicitly names this exact usage** (e.g.
     ADR-0004 names the `/cv/{portfolio_id}` URL) -> leave it, and add a
     one-line comment next to it citing the ADR number. Check what the ADR
     actually pins down, not just the concept it's near -- an ADR covering
     one surface (a URL) doesn't license the same word on a different
     surface (a file name).
4. Unsure whether an ADR covers a specific hit? Treat it as uncovered --
   flag it rather than silently keeping it.

See `EXAMPLE.md` for a worked case: the mistake this skill exists because of.

## Done when

Every `_Avoid_` term present in the diff is either gone, or immediately
followed by an `ADR-000X` citation. Re-grep the diff after your pass to
confirm -- that grep coming up empty (or fully cited) is the completion
criterion, not a sense that you probably got them.

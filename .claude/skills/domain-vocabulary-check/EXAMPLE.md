# Worked example

Ticket 1 renamed the old `dotlist` field to the canonical `skill_list`
(CONTEXT.md: Skill list, `_Avoid_: dotlist, tags, keywords`). The field name
was fixed correctly, but the comment right next to it wasn't:

```python
skill_list: str | None = None  # comma-separated, split into tags in the template
```

"tags" is itself on the `_Avoid_` list -- the rename traded one banned word
for another, one line down. `/code-review` caught it twice: once on the
ticket branch, then again on the PR, because nothing re-ran the check
between the first fix and the merge.

The same ticket also left `template/cv.html` and `main.py`'s
`name="cv.html"` -- "CV" is `_Avoid_` for Portfolio. This is where the ADR
step matters: ADR-0004 deliberately pins the URL `/cv/{portfolio_id}`, so
"cv" *in that URL* is sanctioned. ADR-0004 says nothing about the template
file. `cv.html` should have been `portfolio.html`; the URL was correct as
written.

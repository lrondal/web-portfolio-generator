# Grilling session — surfaced questions

From a `/grill-with-docs` interview sharpening the product direction
(2026-09-01). Four rounds. Kept as the written record of every question the
interview raised — including the ones not thought of before being asked.

## Questions that were surfaced and then decided

Each links to where the decision now lives.

1. **Is "the account that logs in" the same concept as "the person shown on the
   portfolio"?** — No. Split into Account / Profile / Portfolio. See
   `CONTEXT.md`, ADR-0001.
2. **One login → one portfolio, or many?** — Many. One Account owns several
   Portfolios, distinguished only by title. ADR-0001.
3. **SQLite on Render is wiped on every redeploy — where does real data live?**
   — Managed Postgres. ADR-0003.
4. **`/add_user` / `/add_project` let the caller set any `user_id`, including
   the primary key. Who may write what?** — Ownership must come from the
   session, not the request body. *Assumed standard; left unconfirmed when the
   interview stopped — see open questions.*
5. **`/cv/{id}` uses sequential numeric ids — anyone can walk `/cv/1,2,3…` and
   enumerate every user. Keep numeric, or move to a chosen handle?** — Keep
   numeric and always-public, as an accepted trade-off. ADR-0004.
6. **Is a portfolio public the instant it exists, or is there a draft state?** —
   Always public, no draft. ADR-0004.
7. **`dotlist` is a comma-separated string standing in for a list of skills.** —
   Canonical term is "skill list"; `dotlist` is now an `_Avoid_` term.
   `CONTEXT.md`.
8. **One account, several portfolios — what makes them different? A title? A
   purpose? Is one "primary"?** — Title only. Flat list, no primary. ADR-0001.
9. **Does profile info live on each portfolio, or once per account?** — Once per
   Account, reused across all its portfolios. ADR-0001.
10. **Multiple portfolios + always-public + no draft — what stops a
    half-finished portfolio being publicly visible?** — Nothing; accepted.
    ADR-0004.
11. **Email verification on signup — required, or trust the address as typed?**
    — Trust as typed. ADR-0002.
12. **Email+password implies a password-reset flow — in scope?** — Roadmap, not
    v1. ADR-0002, ADR-0005.

## Questions surfaced but still open (interview stopped before Round 4 answers)

13. **Confirm the write boundary:** owning account always derived from the
    logged-in session, and `user_id` removed from the project write payload?
    (Treated as the obvious answer, not explicitly confirmed.)
14. **Delete semantics:** Account → Portfolios → Projects cascade — hard delete
    (rows gone) or soft delete (recoverable)? Current code does a hard cascade.
15. **Project images:** stay as an external URL the owner pastes (no upload, no
    hosting), or is image upload part of the direction?

## Candidate for "a question I had not thought of before it was asked"

Good choices for the oral (pick one and be ready to talk through the reasoning):

- **#1 / #9** — that "the login" and "the person on the page" are different
  things, and that the profile belongs to neither the login nor a single
  portfolio but is shared across all of an account's portfolios.
- **#3** — that a working Render deployment silently loses all data on every
  redeploy, and why that only becomes a problem once there are real accounts.
- **#5 / #10** — that "always public" plus "sequential numeric ids" plus
  "multiple portfolios" together means the whole site is enumerable and there is
  no private workspace, and choosing to accept that on purpose.

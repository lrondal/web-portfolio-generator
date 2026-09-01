---
status: accepted
---

# Account, Profile, and Portfolio are three separate things

The app is self-serve: a person signs up for an **Account** (sign-in email +
password hash) which carries exactly one **Profile** (display name, age, contact
email, GitHub, phone). An Account owns zero or more **Portfolios**, each with its
own title and its own list of Projects; the one Profile is shared across all of
them. The current code merges "the user who logs in" and "the person shown on
the page" into a single `User` row — this decision splits them.

## Considered options

- **One Account = one Portfolio (1:1).** Rejected: the owner wants to publish
  several portfolios (e.g. one per audience) without creating multiple accounts.
- **Profile per Portfolio.** Rejected: the owner preferred a single place to
  edit personal details, accepting that every portfolio then shows the same
  header.

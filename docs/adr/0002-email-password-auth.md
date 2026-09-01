---
status: accepted
---

# Email + password auth, sign-in email trusted as typed

Sign-in is email + password, with the app storing a password hash. The sign-in
email is trusted as entered — no verification link on signup. Chosen over GitHub
OAuth despite a developer audience, to keep the auth flow self-contained and
free of a third-party identity dependency.

## Consequences

- A password-reset flow and signup email verification are needed before real
  use. Both are roadmap, not v1.
- Typo'd sign-in emails will exist and cannot self-serve a reset until that
  roadmap work lands.

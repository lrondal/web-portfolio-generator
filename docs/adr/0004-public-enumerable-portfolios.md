---
status: accepted
---

# Portfolios are always public at an enumerable numeric URL

A Portfolio is reachable at `/cv/{portfolio_id}` with sequential numeric ids, is
public the moment it exists, and has no draft state. A visitor can walk
`/cv/1`, `/cv/2`, … and enumerate every portfolio. This is a deliberate v1
trade-off: the owner judged the simplicity worth more than unguessable URLs or a
publish workflow.

## Consequences

- Total portfolio count and every portfolio's contents are publicly
  discoverable.
- No way to work on a portfolio privately before it is visible.
- Chosen-handle URLs (`/u/{handle}`), an unlisted option, and a draft state
  remain possible later without breaking the model.

---
name: New jurisdiction pack
about: Add statutory late-payment rules for a country
labels: enhancement, good first issue, needs-triage
---

**Country and currency:**

**Statute** (exact name and official source link):

**Interest basis** (reference rate plus uplift, or fixed rate; how the
reference rate is set and how often it changes):

**Fixed compensation** (amount, and whether it scales with debt size):

**Any grace period or preconditions** (for example, interest only runs
after a reminder, or only for business-to-business debts):

A complete pack is one module in `src/chasekit/interest/`, tests with
hand-checkable numbers, and a section in `docs/interest-rules.md`. See
`src/chasekit/interest/uk.py` as the model.

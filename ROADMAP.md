# Roadmap: ChaseKit

Where ChaseKit is going after v0.1.0. This is a plan, not a
promise: items land when they are built, tested, and reviewed, in
roughly this order.

## What v0.2 adds

- **More jurisdictions**, each as one small module with the
  statute cited and hand-checkable tests:
  - US state rules research: there is no US federal statutory
    rate, so v0.2 researches which state-level late-payment
    rules can be encoded honestly, state by state.
  - AU: an Australia pack under the applicable late-payment
    terms and interest rules.
- Stripe and Akaunting invoice sources, next to CSV and
  Invoice Ninja.
- A second template language for the reminder ladder.
- Per-client stage overrides for long-standing relationships.

## Deliberately out of scope

- **It does not create invoices, take payments, or do
  accounting.** ChaseKit is the chasing layer only, on top of
  the tools you already invoice with.
- **Nothing is sent without a human approving the batch.**
  There will never be a fully automatic send mode.
- **No hosted service and no migration.** Your invoices stay in
  your tools; ChaseKit reads exports or your own instance.

## How priorities are set

Priorities are set from GitHub issues and Discussions: open an
issue for concrete, actionable work (a jurisdiction pack starts
with the `new_jurisdiction` issue template), and start a
discussion for ideas and questions.

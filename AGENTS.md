# AGENTS.md

Instructions for AI coding agents (and humans skimming) working in this
repository.

## Layout

- `src/chasekit/` is the package. Pure logic (interest, engine, stages)
  is separated from I/O (sources, senders, store).
- `src/chasekit/interest/` holds one module per jurisdiction pack.
- `src/chasekit/templates/en/` holds the tone-ladder templates.
  Templates are data: edit wording there, not in Python.
- `tests/` mirrors the package. `examples/` holds the demo data and the
  dry-run walkthrough.

## Commands

- Test: `pytest`
- Lint: `ruff check src tests`
- Demo: `chasekit plan --csv examples/invoices.csv --as-of 2026-01-31`

## Conventions

- Zero runtime dependencies. Standard library only.
- Money is always `Decimal`, never float. Interest rounds half-up to
  cents at calculation time.
- Any change to interest or fee logic must cite the statute it encodes
  and ship hand-checkable test numbers.
- Default mode is dry-run everywhere. Nothing in this codebase may send
  a message without the approve path being taken explicitly.
- ChaseKit creates no invoices and does no accounting. Keep that scope.

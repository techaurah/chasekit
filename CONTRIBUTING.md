# Contributing to ChaseKit

Thanks for helping. The two highest-value contribution types are data,
not code:

1. **Jurisdiction packs**: a small module encoding one country's
   statutory interest basis, fixed fees, and grace rules, with tests.
   See `src/chasekit/interest/uk.py` as the model and use the
   `new_jurisdiction` issue template.
2. **Template packs**: tone-ladder wording for a language or culture.
   Markdown only, no code. Use the `new_template_pack` issue template.

New invoice sources (Stripe, Akaunting, generic JSON) implement the one
interface in `src/chasekit/sources/base.py`.

## Dev setup (under 10 minutes)

```bash
git clone https://github.com/techaurah/chasekit.git
cd chasekit
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Python 3.11 or newer. ChaseKit has zero runtime dependencies.

## Rules

- Open an issue before a large change so the shape can be agreed first.
- Every PR links its issue (`Closes #...`) and includes test evidence:
  the command run and its result.
- Interest and fee logic must cite the statute it encodes, in code
  comments and in `docs/interest-rules.md`. A jurisdiction pack without
  a citation and hand-checkable test numbers will not be merged.
- Templates must stay relationship-preserving. No threats the sender
  cannot lawfully or actually carry out, at any stage.
- Run `pytest` and `ruff check src tests` before pushing. CI runs both.

## Review rhythm

Issues are triaged weekly. PRs get a first human response within a few
days. If a claimed good first issue goes quiet for two weeks, it is
unassigned kindly and restocked.

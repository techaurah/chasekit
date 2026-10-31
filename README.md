<h1 align="center">ChaseKit</h1>

<p align="center"><strong>The open-source invoice-chasing layer for freelancers and small businesses.</strong><br/>
ChaseKit detects overdue invoices from the tools you already use, calculates the statutory late-payment interest and fees you are entitled to, and escalates reminders on a tone ladder, with a human approving every send. It is not another invoicing app.</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-0B1F3A?style=flat-square" alt="License: MIT"/>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/Version-0.1.0-00CEFF?style=flat-square" alt="Version 0.1.0"/>
  <img src="https://img.shields.io/badge/Dependencies-zero-2E7D32?style=flat-square" alt="Zero runtime dependencies"/>
</p>

<p align="center">
  <a href="docs/interest-rules.md">Interest Rules</a> ·
  <a href="docs/sources.md">Invoice Sources</a> ·
  <a href="docs/tone-guide.md">Tone Guide</a> ·
  <a href="examples/demo.md">Demo</a> ·
  <a href="https://techaurah.com">TechAurah</a>
</p>

## The problem

Getting paid late is the default. In Intuit QuickBooks' *Small Business Late Payments Report 2025* (vendor research), 56% of US small businesses had outstanding unpaid invoices, and affected businesses were owed an average of $17,500. Yet chasing is still manual, awkward, and inconsistent in most small businesses, because the tools are wrong for them: invoicing suites treat reminders as a paid afterthought and demand you migrate your billing, and dedicated chasing services are closed SaaS locked to specific accounting platforms at a monthly price.

ChaseKit does one job: the chasing layer. It sits on top of whatever you already invoice with. It does **not** create invoices, take payments, or do accounting.

## Demo

ChaseKit running on the example data in `examples/invoices.csv`, pinned to 31 January 2026 (full walkthrough: [examples/demo.md](examples/demo.md)):

```text
Chase plan as of 2026-01-31 (nothing sent):
  INV-1001   Maple Design Studio          stage 1 (friendly), 4 days overdue, interest £1.12, fee £40.00, total £891.12
  INV-1002   Brightpath Consulting        stage 2 (firm), 16 days overdue, interest £12.62, fee £70.00, total £2,482.62
  INV-1003   Koeln Media GmbH             stage 3 (final), 29 days overdue, interest €40.32, fee €40.00, total €5,080.32
  INV-1004   Hartley Construction         stage 4 (escalation), 47 days overdue, interest £185.42, fee £100.00, total £12,285.42
  INV-1007   Denver Dental Group          stage 1 (friendly), 11 days overdue, interest $0.00, fee $0.00, total $1,500.00
```

Every stage shown is one the invoice's age has actually reached, every amount is calculated under the matching jurisdiction's statute, and the US invoice honestly shows $0.00: there is no US federal statutory rate, and none is configured.

## Quickstart

Prerequisites: Python 3.11 or newer. No accounts, no credentials, no network for the demo path.

```bash
git clone https://github.com/techaurah/chasekit.git
cd chasekit
pip install -e .

# See what would be chased (sends nothing, writes nothing)
chasekit --csv examples/invoices.csv --business-name "Your Business" --as-of 2026-01-31 plan

# Render the full batch as a dry run (still sends nothing)
chasekit --csv examples/invoices.csv --business-name "Your Business" --as-of 2026-01-31 run

# See what is outstanding, by age band and by client
chasekit --csv examples/invoices.csv --as-of 2026-01-31 report
```

Sending for real is deliberately a separate, explicit step: configure SMTP (see `.env.example`), then run with `--mode approve`. The batch is listed, you type `YES`, and only then does anything leave the building.

## What it does

- [x] **CSV invoice source**: works with an export from any invoicing tool or spreadsheet ([format](docs/sources.md))
- [x] **Invoice Ninja source**: behind the same interface, for Invoice Ninja users ([honest status](docs/sources.md))
- [x] **Overdue detection** against each invoice's own due date
- [x] **Statutory interest and fixed-fee calculation** per jurisdiction, with the statute cited in code and docs:
  - [x] **UK**: Bank of England base rate + 8%, fixed fee £40 / £70 / £100 (Late Payment of Commercial Debts (Interest) Act 1998)
  - [x] **EU**: reference rate + 8 points, minimum €40 compensation (Directive 2011/7/EU)
  - [x] **US**: configurable rate and fee, zero by default, because there is no federal statute
- [x] **4-stage escalation state machine**: friendly (day 1), firm (day 14), final notice (day 28), escalation handoff (day 42)
- [x] **Tone-ladder templates** in English, relationship-preserving at every stage, rendered with the correct amounts ([tone guide](docs/tone-guide.md))
- [x] **Dry-run by default**: nothing is sent without a human approving the batch
- [x] **SQLite chase log**: who was chased, when, at which stage, with the exact text, so no client is ever chased twice for the same stage
- [x] **CLI report**: outstanding totals by age band and by client, grouped by currency

## Configuration

| Option | Default | What it does |
|---|---|---|
| `--csv` | none | Path to your invoice export (or use `--source invoice-ninja`) |
| `--business-name` | `Your Business` | Name signed on every template |
| `--jurisdiction` | `UK` | Pack for invoices without their own: `UK`, `EU`, `US` |
| `--uk-base-rate` | `4.00` | Bank of England base rate for the half-year the debt's interest period started |
| `--eu-reference-rate` | `2.15` | ECB or national reference rate for the current half-year |
| `--us-rate` / `--us-fee` | `0` / `0` | Your contracted US rate and fee, if you have them |
| `--db` | `chasekit.db` | Chase log location |
| `--as-of` | today | Pin a run to a date (testing and demos) |

Rates are configuration, not constants, because both statutory reference rates change twice a year. [docs/interest-rules.md](docs/interest-rules.md) explains exactly what to check and where.

## Examples

| Example | What it demonstrates | Time | Credentials |
|---|---|---|---|
| [examples/demo.md](examples/demo.md) | Full flow on 7 fake invoices: plan, dry run with a rendered message, report | 5 minutes | None |
| [examples/invoices.csv](examples/invoices.csv) | The CSV format itself, covering all 4 stages, 3 jurisdictions, a not-yet-due and a paid invoice | 1 minute | None |

## Roadmap

**Now (v0.1)**: CSV and Invoice Ninja sources, UK/EU/US packs, English templates, dry-run and approve modes, CLI report.

**Next**: Stripe and Akaunting sources; a second template language; per-client stage overrides.

**Later**: hosted scheduling helpers; more jurisdiction packs as contributors add them (each pack is a small module plus tests, see the `new_jurisdiction` issue template).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), find a `good first issue`, and open a PR that links its issue and passes CI. The two highest-value contributions are data, not code: jurisdiction packs (one small module, statute cited, hand-checkable tests) and template packs (Markdown wording for a language or culture).

## Community and support

| Channel | Best for |
|---|---|
| GitHub Issues | Bugs and feature requests (templates provided) |
| GitHub Discussions | Questions, wording suggestions, show and tell |
| [SECURITY.md](SECURITY.md) | Vulnerabilities, privately, never a public issue |

## License

MIT. See [LICENSE](LICENSE).

## About TechAurah

TechAurah is an AI and software engineering company building AI products, agents, and intelligent automation for businesses in the USA, UK, UAE, Canada, Australia, and Europe.

We are available for AI engineering projects: https://techaurah.com

# Changelog

All notable changes to ChaseKit are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-10-31

### Added

- CSV invoice source (fully working, no credentials needed).
- Invoice Ninja API source behind the same interface. It raises a clear
  not-configured error when no API token is set.
- Overdue detection and a 4-stage escalation state machine driven by days
  overdue: friendly, firm, final notice, escalation handoff.
- Statutory late-payment interest and fixed-fee calculation with three
  jurisdiction packs:
  - UK: Late Payment of Commercial Debts (Interest) Act 1998, Bank of
    England base rate + 8%, fixed fee bands of £40 / £70 / £100.
  - EU: Directive 2011/7/EU, reference rate + 8 percentage points,
    minimum €40 fixed compensation.
  - US: configurable rate and fee, zero by default (no federal statute).
- English tone-ladder template set, one template per stage, rendered with
  the correct principal, interest, fee, and total per invoice.
- Pluggable sender interface. Dry-run is the default mode and nothing is
  sent without explicit approval. An SMTP email sender is included for
  approve mode.
- SQLite chase log recording every planned, dry-run, and sent action, so
  no client is ever chased twice for the same stage.
- CLI with `plan`, `run`, and `report` commands. The report shows
  outstanding totals by age band and by client.
- Worked example (`examples/invoices.csv`) and a dry-run demo walkthrough
  (`examples/demo.md`) that runs fully offline.

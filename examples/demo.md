# Demo: chasing the example invoices, fully offline

This walkthrough runs the whole ChaseKit flow on the fake invoices in
`examples/invoices.csv`. No credentials, no network, and **nothing is
sent**: every step below is plan, dry-run, or report. The `--as-of`
flag pins the run to 31 January 2026 so the output is reproducible.

The example file holds seven invoices. Two are correctly ignored by
every command: INV-1005 is not due yet, and INV-1006 is already paid.

## Setup

```bash
pip install -e .
```

## Step 1: plan (sends nothing, writes nothing)

```bash
chasekit --csv examples/invoices.csv --business-name "Bright Studio" --as-of 2026-01-31 plan
```

```text
Chase plan as of 2026-01-31 (nothing sent):
  INV-1001   Maple Design Studio          stage 1 (friendly), 4 days overdue, interest £1.12, fee £40.00, total £891.12
  INV-1002   Brightpath Consulting        stage 2 (firm), 16 days overdue, interest £12.62, fee £70.00, total £2,482.62
  INV-1003   Koeln Media GmbH             stage 3 (final), 29 days overdue, interest €40.32, fee €40.00, total €5,080.32
  INV-1004   Hartley Construction         stage 4 (escalation), 47 days overdue, interest £185.42, fee £100.00, total £12,285.42
  INV-1007   Denver Dental Group          stage 1 (friendly), 11 days overdue, interest $0.00, fee $0.00, total $1,500.00
```

Read the columns: each overdue invoice is matched to the escalation
stage its age has reached, and the interest and fixed fee are
calculated under its jurisdiction pack. INV-1007 is a US invoice, so
interest and fee are honestly $0.00: there is no federal statutory
rate and none is configured.

## Step 2: dry run (renders every message, sends nothing)

```bash
chasekit --csv examples/invoices.csv --business-name "Bright Studio" --as-of 2026-01-31 run
```

```text
Dry run as of 2026-01-31 (nothing sent):
  INV-1001   Maple Design Studio          stage 1 (friendly), 4 days overdue, interest £1.12, fee £40.00, total £891.12
  INV-1002   Brightpath Consulting        stage 2 (firm), 16 days overdue, interest £12.62, fee £70.00, total £2,482.62
  INV-1003   Koeln Media GmbH             stage 3 (final), 29 days overdue, interest €40.32, fee €40.00, total €5,080.32
  INV-1004   Hartley Construction         stage 4 (escalation), 47 days overdue, interest £185.42, fee £100.00, total £12,285.42
  INV-1007   Denver Dental Group          stage 1 (friendly), 11 days overdue, interest $0.00, fee $0.00, total $1,500.00
DRY RUN: no email was sent. Review the batch, then re-run with --mode approve to send it.
```

This is the exact stage 2 message the dry run produced for INV-1002:

```text
Subject: Invoice INV-1002 is now 16 days overdue

Hi Sam Reed,

I wrote recently about invoice INV-1002 for £2,400.00, due on
2026-01-15. It is still unpaid, now 16 days past due, and I have not
heard back.

The balance now stands as follows:

- Invoice amount: £2,400.00
- Late payment interest: £12.62
- Fixed compensation: £70.00
- Total now due: £2,482.62

Interest and compensation are calculated on this basis: Bank of
England base rate (4.00%) + 8% statutory interest, and fixed
compensation under the Late Payment of Commercial Debts (Interest)
Act 1998.

Please arrange payment of £2,482.62 within the next 7 days, or reply
and tell me when it will be paid. If there is a problem with the
invoice itself, raise it now and I will deal with it straight away.
What I cannot do is leave it unanswered.

Kind regards,

Bright Studio
```

The dry run is recorded in the SQLite chase log with status `dry_run`.
It does **not** block anything: run the plan again and the same batch
appears, ready for a real decision.

## Step 3: report (what is outstanding, by age and by client)

```bash
chasekit --csv examples/invoices.csv --as-of 2026-01-31 report
```

```text
Outstanding report as of 2026-01-31

By age band:
  1-7 days   1 invoice(s): £891.12
  8-14 days  1 invoice(s): $1,500.00
  15-30 days 2 invoice(s): €5,080.32; £2,482.62
  31-60 days 1 invoice(s): £12,285.42

By client:
  Brightpath Consulting: 1 invoice(s), oldest 16 days. £2,482.62
  Denver Dental Group: 1 invoice(s), oldest 11 days. $1,500.00
  Hartley Construction: 1 invoice(s), oldest 47 days. £12,285.42
  Koeln Media GmbH: 1 invoice(s), oldest 29 days. €5,080.32
  Maple Design Studio: 1 invoice(s), oldest 4 days. £891.12

Total outstanding (principal + interest + fees): €5,080.32; £15,659.16; $1,500.00
```

Totals are grouped by currency. ChaseKit never invents an exchange
rate to force a single headline number.

## Step 4 (not run here): sending for real

```bash
export CHASEKIT_SMTP_HOST=...   # plus the other CHASEKIT_SMTP_* values, see .env.example
chasekit --csv examples/invoices.csv --business-name "Bright Studio" run --mode approve
```

Approve mode lists the batch, waits for you to type `YES`, sends via
SMTP, and records each message as `sent`. A stage recorded as sent is
never planned again for that invoice: nobody gets chased twice for the
same stage.

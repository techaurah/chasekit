# Invoice sources

ChaseKit sits on top of whatever a business already invoices with. It
never creates invoices. A source only has to answer one question: what
invoices exist, and which of them are paid?

## CSV source (fully working)

The universal denominator: every invoicing tool, accounting package,
and spreadsheet can export a CSV. This source is complete, tested, and
needs no credentials.

```bash
chasekit plan --csv invoices.csv
```

### Format

| Column | Required | Notes |
|---|---|---|
| `invoice_number` | Yes | Your reference, e.g. `INV-1042` |
| `client_name` | Yes | Business being chased |
| `client_email` | Yes | Where reminders are sent |
| `amount` | Yes | Invoice total, e.g. `1250.00` |
| `currency` | Yes | ISO code: `GBP`, `EUR`, `USD` |
| `due_date` | Yes | `YYYY-MM-DD` |
| `contact_name` | No | Greeting name; defaults to the client name |
| `issue_date` | No | `YYYY-MM-DD`, recorded for context |
| `status` | No | `paid` (any case) counts as paid; anything else is unpaid |
| `jurisdiction` | No | `UK`, `EU`, or `US`; blank uses the configured default |

See `examples/invoices.csv` for a complete worked file.

## Invoice Ninja source (interface implemented, credentials required)

For self-hosted or cloud Invoice Ninja users:

```bash
export CHASEKIT_INVOICE_NINJA_URL=https://ninja.example.com
export CHASEKIT_INVOICE_NINJA_TOKEN=your-api-token
export CHASEKIT_INVOICE_NINJA_CURRENCY=GBP   # optional, default USD
chasekit plan --source invoice-ninja
```

Create the token in Invoice Ninja under Settings, then API Tokens.
ChaseKit reads invoices with client data via `GET /api/v1/invoices`
and maps number, amount, due date, paid status (`status_id` 4), client
name, and first contact email. The Invoice Ninja API returns a numeric
currency ID rather than an ISO code, so the account currency is taken
from `CHASEKIT_INVOICE_NINJA_CURRENCY` instead of guessed.

Honest status: this source is **not** covered by the automated tests or
the demo, because both run offline with no Invoice Ninja instance. With
no credentials set it raises a clear error saying exactly what to
configure, rather than failing obscurely. Reports from users running it
against a real instance are very welcome (that is the fastest route to
removing this caveat).

## Adding a source

Implement `load() -> list[Invoice]` from
`src/chasekit/sources/base.py` (a one-method protocol). Stripe,
Akaunting, and generic JSON are natural next sources. Detection,
interest, templates, logging, and sending all work unchanged.

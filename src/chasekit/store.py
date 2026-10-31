"""SQLite chase log.

Every planned, dry-run, and sent action is recorded. Only actions with
status "sent" count for duplicate prevention: a dry run never blocks a
later real send, and a real send permanently blocks a repeat of the
same stage for the same invoice.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS chase_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT NOT NULL,
    client_email TEXT NOT NULL,
    stage INTEGER NOT NULL,
    status TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chase_log_invoice_stage
    ON chase_log (invoice_number, stage, status);
"""


class ChaseStore:
    def __init__(self, db_path: str | Path = "chasekit.db") -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def has_sent(self, invoice_number: str, stage: int) -> bool:
        """True if this stage was already really sent for this invoice."""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM chase_log"
            " WHERE invoice_number = ? AND stage = ? AND status = 'sent'",
            (invoice_number, stage),
        ).fetchone()
        return bool(row and row[0] > 0)

    def record(
        self,
        invoice_number: str,
        client_email: str,
        stage: int,
        status: str,
        subject: str,
        body: str,
    ) -> None:
        self._conn.execute(
            "INSERT INTO chase_log"
            " (invoice_number, client_email, stage, status, subject, body, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                invoice_number,
                client_email,
                stage,
                status,
                subject,
                body,
                datetime.now(UTC).isoformat(timespec="seconds"),
            ),
        )
        self._conn.commit()

    def history(self, invoice_number: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT stage, status, subject, created_at FROM chase_log"
            " WHERE invoice_number = ? ORDER BY id",
            (invoice_number,),
        ).fetchall()
        return [
            {"stage": r[0], "status": r[1], "subject": r[2], "created_at": r[3]}
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()

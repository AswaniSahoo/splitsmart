"""SQLite persistence for SplitSmart (standard-library sqlite3, no ORM)."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from typing import Any

from splitsmart.ledger import Expense, split_equal

SCHEMA = """
CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS members (
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    PRIMARY KEY (group_id, name)
);
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    payer TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS expense_participants (
    expense_id INTEGER NOT NULL REFERENCES expenses(id) ON DELETE CASCADE,
    member TEXT NOT NULL,
    position INTEGER NOT NULL,
    PRIMARY KEY (expense_id, member)
);
"""


def _clean_name(name: str) -> str:
    cleaned = name.strip() if isinstance(name, str) else ""
    if not cleaned:
        raise ValueError("names must be non-empty")
    if len(cleaned) > 60:
        raise ValueError("names must be at most 60 characters")
    return cleaned


class Store:
    def __init__(self, path: str | None = None) -> None:
        env_path = os.environ.get("SPLITSMART_DB", "").strip()
        # Treat an empty or unexpanded "${...}" value as unset; "" would make SQLite use a throwaway DB.
        if not env_path or env_path.startswith("${"):
            env_path = "splitsmart.db"
        self.path = path or env_path
        with closing(self._connect()) as conn, conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ---- groups & members -------------------------------------------------
    def create_group(self, name: str, members: list[str]) -> dict[str, Any]:
        name = _clean_name(name)
        cleaned = [_clean_name(m) for m in members]
        if not cleaned:
            raise ValueError("a group needs at least one member")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("member names must be unique")
        with closing(self._connect()) as conn, conn:
            gid = conn.execute("INSERT INTO groups(name) VALUES (?)", (name,)).lastrowid
            conn.executemany("INSERT INTO members(group_id, name) VALUES (?, ?)", [(gid, m) for m in cleaned])
        return self.get_group(gid)

    def list_groups(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT id, name FROM groups ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def _require_group(self, conn: sqlite3.Connection, group_id: int) -> sqlite3.Row:
        row = conn.execute("SELECT id, name FROM groups WHERE id = ?", (group_id,)).fetchone()
        if row is None:
            raise KeyError(f"group {group_id} not found")
        return row

    def members(self, group_id: int) -> list[str]:
        with closing(self._connect()) as conn:
            self._require_group(conn, group_id)
            rows = conn.execute(
                "SELECT name FROM members WHERE group_id = ? ORDER BY rowid", (group_id,)
            ).fetchall()
        return [r["name"] for r in rows]

    def add_member(self, group_id: int, name: str) -> dict[str, Any]:
        name = _clean_name(name)
        with closing(self._connect()) as conn, conn:
            self._require_group(conn, group_id)
            try:
                conn.execute("INSERT INTO members(group_id, name) VALUES (?, ?)", (group_id, name))
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"member {name!r} already exists") from exc
        return self.get_group(group_id)

    # ---- expenses ---------------------------------------------------------
    def add_expense(
        self,
        group_id: int,
        description: str,
        amount_cents: int,
        payer: str,
        participants: list[str],
    ) -> dict[str, Any]:
        description = _clean_name(description)
        members = set(self.members(group_id))
        split_equal(amount_cents, participants)  # validates amount + participants
        unknown = [p for p in [payer, *participants] if p not in members]
        if unknown:
            raise ValueError(f"not group members: {', '.join(sorted(set(unknown)))}")
        with closing(self._connect()) as conn, conn:
            eid = conn.execute(
                "INSERT INTO expenses(group_id, description, amount_cents, payer) VALUES (?, ?, ?, ?)",
                (group_id, description, amount_cents, payer),
            ).lastrowid
            conn.executemany(
                "INSERT INTO expense_participants(expense_id, member, position) VALUES (?, ?, ?)",
                [(eid, p, i) for i, p in enumerate(participants)],
            )
        return {
            "id": eid,
            "description": description,
            "amount_cents": amount_cents,
            "payer": payer,
            "participants": list(participants),
        }

    def delete_expense(self, group_id: int, expense_id: int) -> None:
        with closing(self._connect()) as conn, conn:
            self._require_group(conn, group_id)
            cur = conn.execute("DELETE FROM expenses WHERE id = ? AND group_id = ?", (expense_id, group_id))
            if cur.rowcount == 0:
                raise KeyError(f"expense {expense_id} not found")

    def expenses(self, group_id: int) -> list[dict[str, Any]]:
        with closing(self._connect()) as conn:
            self._require_group(conn, group_id)
            rows = conn.execute(
                "SELECT id, description, amount_cents, payer FROM expenses WHERE group_id = ? ORDER BY id",
                (group_id,),
            ).fetchall()
            result = []
            for r in rows:
                parts = conn.execute(
                    "SELECT member FROM expense_participants WHERE expense_id = ? ORDER BY position",
                    (r["id"],),
                ).fetchall()
                result.append({**dict(r), "participants": [p["member"] for p in parts]})
        return result

    def ledger_expenses(self, group_id: int) -> list[Expense]:
        return [
            Expense(e["description"], e["amount_cents"], e["payer"], tuple(e["participants"]))
            for e in self.expenses(group_id)
        ]

    def get_group(self, group_id: int) -> dict[str, Any]:
        with closing(self._connect()) as conn:
            row = self._require_group(conn, group_id)
        return {
            "id": row["id"],
            "name": row["name"],
            "members": self.members(group_id),
            "expenses": self.expenses(group_id),
        }

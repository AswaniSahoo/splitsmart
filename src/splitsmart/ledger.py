"""Pure domain logic for SplitSmart.

All money values are integer minor units (cents/paise). This module performs no I/O
and must not import FastAPI, sqlite3 or mcp.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Expense:
    description: str
    amount_cents: int
    payer: str
    participants: tuple[str, ...]


@dataclass(frozen=True)
class Transfer:
    from_member: str
    to_member: str
    amount_cents: int


def split_equal(amount_cents: int, participants: list[str] | tuple[str, ...]) -> dict[str, int]:
    """Split an amount equally; leftover cents go one each to participants in listed order."""
    if not isinstance(amount_cents, int) or isinstance(amount_cents, bool) or amount_cents <= 0:
        raise ValueError("amount_cents must be a positive integer")
    if not participants:
        raise ValueError("an expense needs at least one participant")
    if len(set(participants)) != len(participants):
        raise ValueError("participants must be distinct")
    base, remainder = divmod(amount_cents, len(participants))
    return {name: base + (1 if i < remainder else 0) for i, name in enumerate(participants)}


def compute_balances(members: Iterable[str], expenses: Iterable[Expense]) -> dict[str, int]:
    """Net balance per member: total paid minus total share owed."""
    balances = {m: 0 for m in members}
    for exp in expenses:
        if exp.payer not in balances:
            raise ValueError(f"unknown payer: {exp.payer}")
        shares = split_equal(exp.amount_cents, exp.participants)
        for name, share in shares.items():
            if name not in balances:
                raise ValueError(f"unknown participant: {name}")
            balances[name] -= share
        balances[exp.payer] += exp.amount_cents
    return balances


def settle_up(balances: dict[str, int]) -> list[Transfer]:
    """Greedy settle-up: match the largest debtor with the largest creditor until all are zero.

    Each transfer zeroes at least one member, so there are at most (non-zero members - 1) transfers.
    """
    if sum(balances.values()) != 0:
        raise ValueError("balances must sum to zero")
    remaining = {m: b for m, b in balances.items() if b != 0}
    transfers: list[Transfer] = []
    while remaining:
        # Ties broken by name so the plan is deterministic.
        debtor = min(remaining, key=lambda m: (remaining[m], m))
        creditor = max(remaining, key=lambda m: (remaining[m], m))
        amount = min(-remaining[debtor], remaining[creditor])
        transfers.append(Transfer(debtor, creditor, amount))
        remaining[debtor] += amount
        remaining[creditor] -= amount
        for m in (debtor, creditor):
            if remaining[m] == 0:
                del remaining[m]
    return transfers


def format_cents(amount_cents: int) -> str:
    """Format integer cents as a decimal string with two places, e.g. -1234 -> "-12.34"."""
    sign = "-" if amount_cents < 0 else ""
    whole, frac = divmod(abs(amount_cents), 100)
    return f"{sign}{whole}.{frac:02d}"

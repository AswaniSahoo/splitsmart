"""MCP server exposing SplitSmart operations as tools (stdio transport)."""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from splitsmart.ledger import compute_balances, format_cents
from splitsmart.ledger import settle_up as _settle_up
from splitsmart.store import Store


def build_server(store: Store | None = None) -> MCPServer:
    db = store or Store()
    server = MCPServer(
        name="splitsmart",
        instructions=(
            "Manage shared group expenses. All money is integer cents (e.g. 12.50 = 1250). "
            "Create a group, add expenses, then call get_balances or settle_up."
        ),
    )

    @server.tool()
    def create_group(name: str, members: list[str]) -> dict[str, Any]:
        """Create a group with a name and a list of unique member names."""
        return db.create_group(name, members)

    @server.tool()
    def list_groups() -> list[dict[str, Any]]:
        """List all groups (id and name)."""
        return db.list_groups()

    @server.tool()
    def get_group(group_id: int) -> dict[str, Any]:
        """Get a group with its members and expenses."""
        return db.get_group(group_id)

    @server.tool()
    def add_member(group_id: int, name: str) -> dict[str, Any]:
        """Add a new member to an existing group."""
        return db.add_member(group_id, name)

    @server.tool()
    def add_expense(
        group_id: int, description: str, amount_cents: int, payer: str, participants: list[str]
    ) -> dict[str, Any]:
        """Record an expense paid by `payer`, split equally among `participants`. amount_cents is a positive integer."""
        return db.add_expense(group_id, description, amount_cents, payer, participants)

    @server.tool()
    def delete_expense(group_id: int, expense_id: int) -> str:
        """Delete an expense from a group."""
        db.delete_expense(group_id, expense_id)
        return f"deleted expense {expense_id}"

    @server.tool()
    def get_balances(group_id: int) -> list[dict[str, Any]]:
        """Net balance per member in cents: positive = is owed money, negative = owes money."""
        bal = compute_balances(db.members(group_id), db.ledger_expenses(group_id))
        return [{"member": m, "balance_cents": b, "display": format_cents(b)} for m, b in bal.items()]

    @server.tool()
    def settle_up(group_id: int) -> list[dict[str, Any]]:
        """Minimal list of transfers (from, to, amount_cents) that settles every debt in the group."""
        bal = compute_balances(db.members(group_id), db.ledger_expenses(group_id))
        return [
            {
                "from": t.from_member,
                "to": t.to_member,
                "amount_cents": t.amount_cents,
                "display": format_cents(t.amount_cents),
            }
            for t in _settle_up(bal)
        ]

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()

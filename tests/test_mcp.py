"""In-process smoke test for the MCP server tools."""

import json

import anyio

from splitsmart.mcp_server import build_server
from splitsmart.store import Store


def _payload(result):
    """Return the structured output of a CallToolResult (list results are wrapped in {"result": ...})."""
    assert not result.is_error, result.content
    data = result.structured_content
    if isinstance(data, dict) and set(data) == {"result"}:
        return data["result"]
    return data if data is not None else json.loads(result.content[0].text)


def test_mcp_tools_end_to_end(tmp_path):
    server = build_server(Store(str(tmp_path / "mcp.db")))

    async def run():
        names = {t.name for t in await server.list_tools()}
        assert {
            "create_group",
            "list_groups",
            "get_group",
            "add_member",
            "add_expense",
            "delete_expense",
            "get_balances",
            "settle_up",
        } <= names

        g = _payload(await server.call_tool("create_group", {"name": "Flat", "members": ["A", "B"]}))
        gid = g["id"]

        groups = _payload(await server.call_tool("list_groups", {}))
        assert any(x["id"] == gid and x["name"] == "Flat" for x in groups)

        _payload(await server.call_tool("add_member", {"group_id": gid, "name": "C"}))
        group = _payload(await server.call_tool("get_group", {"group_id": gid}))
        assert group["members"] == ["A", "B", "C"]
        assert group["expenses"] == []

        expense = _payload(
            await server.call_tool(
                "add_expense",
                {
                    "group_id": gid,
                    "description": "Rent",
                    "amount_cents": 3000,
                    "payer": "A",
                    "participants": ["A", "B", "C"],
                },
            )
        )
        eid = expense["id"]

        bal = {
            b["member"]: b["balance_cents"]
            for b in _payload(await server.call_tool("get_balances", {"group_id": gid}))
        }
        assert bal == {"A": 2000, "B": -1000, "C": -1000}

        plan = _payload(await server.call_tool("settle_up", {"group_id": gid}))
        assert sorted((t["from"], t["to"], t["amount_cents"]) for t in plan) == [
            ("B", "A", 1000),
            ("C", "A", 1000),
        ]

        delete_result = _payload(
            await server.call_tool("delete_expense", {"group_id": gid, "expense_id": eid})
        )
        assert delete_result == f"deleted expense {eid}"

        bal_after = _payload(await server.call_tool("get_balances", {"group_id": gid}))
        assert all(b["balance_cents"] == 0 for b in bal_after)
        assert _payload(await server.call_tool("settle_up", {"group_id": gid})) == []

    anyio.run(run)

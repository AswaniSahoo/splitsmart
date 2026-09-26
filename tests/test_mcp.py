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
        assert {"create_group", "add_expense", "get_balances", "settle_up"} <= names
        g = _payload(await server.call_tool("create_group", {"name": "Flat", "members": ["A", "B"]}))
        await server.call_tool(
            "add_expense",
            {
                "group_id": g["id"],
                "description": "Rent",
                "amount_cents": 2000,
                "payer": "A",
                "participants": ["A", "B"],
            },
        )
        plan = _payload(await server.call_tool("settle_up", {"group_id": g["id"]}))
        assert plan == [{"from": "B", "to": "A", "amount_cents": 1000, "display": "10.00"}]

    anyio.run(run)

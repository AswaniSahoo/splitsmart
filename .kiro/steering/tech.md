---
inclusion: always
---

# Tech stack

- Python 3.12, managed with `uv` (never call `pip` directly; use `uv add` / `uv run`).
- FastAPI + Uvicorn for the HTTP API; the web UI is a single static `index.html` with vanilla JS (no build step).
- SQLite via the standard-library `sqlite3` module (no ORM).
- MCP server built with the official `mcp` Python SDK v2 (`from mcp.server.mcpserver import MCPServer`), stdio transport.
- Tests: `pytest` for example tests, `hypothesis` for property-based tests.
- Lint/format: `ruff` (`uv run ruff check --fix` and `uv run ruff format`).

## Common commands
- Run app: `uv run splitsmart` (serves on http://127.0.0.1:8000)
- Run MCP server: `uv run splitsmart-mcp`
- Tests: `uv run pytest -q`
- Lint: `uv run ruff check .`

## Constraints
- Keep dependencies minimal; pin exact versions when adding new ones.
- Pure business logic lives in `splitsmart/ledger.py` and must not import FastAPI, sqlite3 or mcp.

# SplitSmart 💸

Split group expenses fairly — from a web page, a REST API, or straight from your AI agent via MCP.
Record who paid, see who owes whom, and get the **fewest transfers** needed to settle up.
All money math is done in integer paise/cents, and the core rules are proven with property-based tests.

Built with [Kiro](https://kiro.dev) for the **Kiro University Challenge** (#KiroUniversity #BuildWithKiro).

## Quick start

```bash
git clone https://github.com/AswaniSahoo/splitsmart && cd splitsmart
uv sync
uv run splitsmart          # web UI + API at http://127.0.0.1:8000
uv run pytest -q           # 21 tests incl. 7 property-based tests
uv run splitsmart-mcp      # MCP server (stdio) — normally started by Kiro via .kiro/settings/mcp.json
```

Use it from Kiro CLI with the custom agent:

```bash
kiro-cli chat --agent splitsmart-accountant
> Create a group Goa Trip with Asha, Ravi and Meera. Asha paid ₹1200 for the hotel for all three. Who owes whom?
```

> ⚠️ SplitSmart has **no authentication** and binds to `127.0.0.1` by default. Don't expose it to the internet.

## How each Kiro lesson is used

| # | Lesson | Where | What it does in this project |
|---|---|---|---|
| 1 | Spec-driven development | [`.kiro/specs/expense-splitter/`](.kiro/specs/expense-splitter) | EARS requirements → design (architecture, API, data model) → task plan that drove the build |
| 2 | Steering | [`.kiro/steering/`](.kiro/steering) | `product.md`, `tech.md`, `structure.md` (always) + `money-handling.md` (fileMatch on Python files) enforcing integer-cents money |
| 3 | Hooks | [`.kiro/hooks/`](.kiro/hooks) | `PostFileSave` ruff + re-run PBTs when `ledger.py` changes, `PostTaskExec` full test run, `Stop` (agent stop) money-safety self-check, `PreToolUse` guard blocking `rm -rf` / DB deletion |
| 4 | Property-based testing | [`design.md` → Correctness Properties](.kiro/specs/expense-splitter/design.md), [`tests/test_ledger_properties.py`](tests/test_ledger_properties.py) | 7 properties (money conserved, balances sum to 0, order independence, delete = undo, settle-up clears debts, ≤ n−1 transfers, format round-trip) run with Hypothesis, 200–500 cases each |
| 5 | Powers | Kiro Powers panel | Installed the **Context7** power from the Kiro registry and used it to check `tests/test_ledger_properties.py` against the current Hypothesis `@settings` / `max_examples` docs; also installed our own SplitSmart power (Bonus 2) |
| 6 | MCP | [`src/splitsmart/mcp_server.py`](src/splitsmart/mcp_server.py), [`.kiro/settings/mcp.json`](.kiro/settings/mcp.json) | Our own MCP server exposing 8 tools (`create_group`, `add_expense`, `get_balances`, `settle_up`, …) + `fetch` server; read-only tools auto-approved |
| 7 | Custom agents | [`.kiro/agents/`](.kiro/agents) | `splitsmart-accountant` (MCP-only, no shell/writes, asks before mutating data) and `splitsmart-dev` (scoped shell/write permissions, steering + spec as resources, own hooks) |
| ★1 | Kiro Web, cloud sessions, cloud configuration | [PR #1](https://github.com/AswaniSahoo/splitsmart/pull/1), [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Uploaded local `~/.kiro/powers` (SplitSmart + Context7) via Kiro Web **Configuration Sync**; started a **cloud session** from the IDE (Agent Focus) on this repo, which followed the cloned `.kiro/steering`, ran ruff + all tests in the sandbox and opened PR #1 adding GitHub Actions CI |
| ★2 | Package a Kiro power | [`power-splitsmart/`](power-splitsmart) | `plugin.json` manifest + `mcp.json` (runs SplitSmart MCP from GitHub via `uvx`) + 2 skills (`split-expenses`, `run-splitsmart`) |

Install the power in Kiro: **Powers panel → Add Custom Power → Import power from GitHub →**
`https://github.com/AswaniSahoo/splitsmart` (power folder: `power-splitsmart`), then say *"split the dinner bill"*.

## Architecture

```
Web UI ──fetch──▶ api.py (FastAPI) ─┐
                                     ├─▶ store.py (SQLite) + ledger.py (pure money logic)
Kiro agent ─MCP─▶ mcp_server.py ─────┘
```

## API

| Method | Path | Body |
|---|---|---|
| POST | `/api/groups` | `{name, members[]}` |
| GET | `/api/groups`, `/api/groups/{id}` | |
| POST | `/api/groups/{id}/members` | `{name}` |
| POST | `/api/groups/{id}/expenses` | `{description, amount_cents, payer, participants[]}` |
| DELETE | `/api/groups/{id}/expenses/{expense_id}` | |
| GET | `/api/groups/{id}/balances`, `/api/groups/{id}/settle` | |

## License

MIT

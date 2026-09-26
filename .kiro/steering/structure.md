---
inclusion: always
---

# Project structure

```
src/splitsmart/
  ledger.py      # pure domain logic: split, balances, settle-up (no I/O)
  store.py       # SQLite persistence (groups, members, expenses)
  api.py         # FastAPI app + routes; thin layer over store + ledger
  mcp_server.py  # MCP server exposing the same operations as tools
  static/index.html  # one-page web UI
tests/
  test_ledger_properties.py  # hypothesis property-based tests
  test_api.py                # API example tests
power-splitsmart/  # the Kiro power packaged from this project (Bonus 2)
```

## Conventions
- Layering: `api.py` and `mcp_server.py` call `store.py` and `ledger.py`; `ledger.py` calls nothing.
- Every new feature starts as a spec in `.kiro/specs/`.
- Functions and modules use `snake_case`; Pydantic models use `PascalCase`.
- Type hints on every public function.

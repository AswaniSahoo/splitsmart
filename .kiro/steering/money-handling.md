---
inclusion: fileMatch
fileMatchPattern: ["src/splitsmart/**/*.py", "tests/**/*.py"]
---

# Money handling standard

Enforce that all money amounts are stored and computed as **integer minor units (paise/cents)**, never as `float`,
so that balances always sum to exactly zero and no rupee or cent is lost or invented by rounding errors.

For example, splitting ₹100.00 three ways:

```python
# WRONG - float math drifts and loses money
share = 100.00 / 3  # 33.333333...
total = share * 3  # 99.99999999999999

# RIGHT - integer paise; the leftover paise go to the first members deterministically
amount = 10000  # ₹100.00 in paise
base, remainder = divmod(amount, 3)
shares = [base + (1 if i < remainder else 0) for i in range(3)]  # [3334, 3333, 3333]
assert sum(shares) == amount
```

ensures integer minor units are used for all money everywhere.

## Rules
- API/MCP inputs and outputs use integer `amount_cents` fields. Convert to a decimal string only for display in the UI.
- Never use `float` for money in `ledger.py`, `store.py`, `api.py` or `mcp_server.py`.
- Amounts must be positive integers (> 0); reject zero or negative amounts with a clear validation error.
- Remainder paise are distributed one each to participants in the order they are listed.

---
name: split-expenses
description: Use when the user wants to split a bill, record a shared expense, see who owes whom, or settle up a group (trip, flat, dinner) with the SplitSmart MCP tools.
---

# Split group expenses with SplitSmart

## Step 1: Find or create the group
- Call `list_groups`. If the user's group exists, call `get_group` to see members.
- Otherwise call `create_group` with a name and the list of unique member names.

## Step 2: Convert money to integer cents
All SplitSmart amounts are integer minor units. Convert before calling tools:
- "₹1,200" → `120000`, "$12.50" → `1250`, "45.5" → `4550`.
- Never pass floats. Reject zero or negative amounts and ask the user to correct them.
See `references/money-rules.md` for rounding rules.

## Step 3: Record each expense
Call `add_expense(group_id, description, amount_cents, payer, participants)`.
- `payer` and every participant must already be members — add missing people with `add_member` first.
- If the user says "split between everyone", pass every member as participants.

## Step 4: Report results
Call `get_balances` and `settle_up`, then show:

| Member | Balance |
|---|---|
| Asha | +₹66.66 (is owed) |
| Ravi | -₹33.33 (owes) |

followed by the transfers, e.g. "Ravi pays Asha ₹33.33".

## Step 5: Fix mistakes
Use `get_group` to find the expense id, then `delete_expense` and re-add it correctly.
Deleting an expense restores balances exactly as if it had never been added.

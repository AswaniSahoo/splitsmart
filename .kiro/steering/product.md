---
inclusion: always
---

# Product: SplitSmart

SplitSmart is a small, self-hosted expense splitter for friend groups, trips and flatmates.

## Users
- Small groups (2–20 people) who share costs and want to know "who owes whom".
- Developers who want to manage group expenses from an AI agent via MCP.

## Core features
- Create a group with members.
- Record an expense: who paid, how much, and which members share it (equal split).
- See each member's net balance (positive = is owed money, negative = owes money).
- Get a minimal "settle up" plan: the fewest practical transfers that clear all debts.
- Same features exposed through a REST API, a one-page web UI, and an MCP server.

## Non-goals
- No authentication, payments, currency conversion or multi-currency groups.
- Not meant to be exposed on the public internet (local / trusted network use only).

# Requirements Document

## Introduction

SplitSmart lets a small group record shared expenses and work out who owes whom, with a minimal set of
transfers to settle up. It is available as a REST API, a one-page web UI, and an MCP server so AI agents
(such as Kiro) can manage group expenses. All money is handled as integer minor units (cents/paise).

## Glossary

- **Group**: a named set of members who share expenses.
- **Member**: a person in a group, identified by a unique (per group) non-empty name.
- **Expense**: an amount paid by one member (the payer) and shared equally by one or more members (participants).
- **Balance**: for a member, total paid minus total owed share. Positive = is owed, negative = owes.
- **Settlement**: a transfer `from → to` of an amount that reduces debts.

## Requirements

### Requirement 1: Groups and members

**User Story:** As a trip organiser, I want to create a group with its members, so that we can track shared costs.

#### Acceptance Criteria

1. WHEN a user creates a group with a name and at least one member name THE SYSTEM SHALL store the group and return its id and members.
2. WHEN a user creates a group with duplicate member names THE SYSTEM SHALL reject the request with a validation error.
3. WHEN a user adds a new member to an existing group THE SYSTEM SHALL add the member with a balance of 0.
4. WHEN a user requests a group that does not exist THE SYSTEM SHALL respond with a not-found error.

### Requirement 2: Recording expenses

**User Story:** As a group member, I want to record who paid for something and who shared it, so that the cost is split fairly.

#### Acceptance Criteria

1. WHEN a user records an expense with a description, a positive integer `amount_cents`, a payer and one or more participants who are all group members THE SYSTEM SHALL store the expense.
2. WHEN an expense is recorded THE SYSTEM SHALL split the amount equally among participants in integer cents, giving any remainder cents one each to participants in listed order, so that the shares sum exactly to the amount.
3. IF the amount is zero or negative THEN THE SYSTEM SHALL reject the expense with a validation error.
4. IF the payer or any participant is not a member of the group THEN THE SYSTEM SHALL reject the expense with a validation error.
5. WHEN a user deletes an expense THE SYSTEM SHALL remove it and balances SHALL be as if it had never been recorded.

### Requirement 3: Balances

**User Story:** As a group member, I want to see everyone's net balance, so that I know who owes money and who is owed.

#### Acceptance Criteria

1. WHEN a user requests balances for a group THE SYSTEM SHALL return, for each member, total paid minus total share owed, in integer cents.
2. THE SYSTEM SHALL ensure that the sum of all member balances in a group is exactly 0.
3. WHEN balances are computed THE SYSTEM SHALL produce the same result regardless of the order in which expenses were recorded.

### Requirement 4: Settle-up plan

**User Story:** As a group member, I want a short list of payments that settles all debts, so that we can square up quickly.

#### Acceptance Criteria

1. WHEN a user requests a settle-up plan THE SYSTEM SHALL return a list of transfers (`from`, `to`, `amount_cents`) with every amount a positive integer.
2. WHEN all transfers in the plan are applied to the balances THE SYSTEM SHALL leave every member with a balance of exactly 0.
3. THE SYSTEM SHALL produce a plan with at most (number of members with non-zero balance − 1) transfers.
4. THE SYSTEM SHALL only create transfers from members with negative balance to members with positive balance.
5. WHEN all balances are already 0 THE SYSTEM SHALL return an empty plan.

### Requirement 5: Access surfaces

**User Story:** As a user or AI agent, I want to use SplitSmart from a browser, HTTP or MCP, so that I can pick the interface that suits me.

#### Acceptance Criteria

1. THE SYSTEM SHALL expose groups, expenses, balances and settle-up through a JSON REST API.
2. THE SYSTEM SHALL serve a one-page web UI at `/` that uses the REST API.
3. THE SYSTEM SHALL expose the same operations as MCP tools over stdio, backed by the same SQLite database.
4. THE SYSTEM SHALL format money for display as a decimal string with two places (e.g. 1234 → "12.34") only at the presentation layer.

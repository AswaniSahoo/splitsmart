# Implementation Plan

- [x] 1. Set up project structure
  - uv project, FastAPI, mcp, pytest, hypothesis, ruff
  - _Requirements: 5.1_

- [x] 2. Implement pure ledger logic
  - [x] 2.1 Implement `split_equal`, `compute_balances`, `settle_up`, `format_cents` in `ledger.py`
    - _Requirements: 2.2, 3.1, 3.2, 3.3, 4.1–4.5, 5.4_
  - [x]* 2.2 Write property test for split conservation
    - **Property 1: Split conserves money**
    - **Validates: Requirements 2.2**
  - [x]* 2.3 Write property test for balances summing to zero
    - **Property 2: Balances sum to zero**
    - **Validates: Requirements 3.1, 3.2**
  - [x]* 2.4 Write property test for order independence
    - **Property 3: Balances are order-independent**
    - **Validates: Requirements 3.3**
  - [x]* 2.5 Write property test for delete-as-undo
    - **Property 4: Deleting an expense is a perfect undo**
    - **Validates: Requirements 2.5**
  - [x]* 2.6 Write property test for settle-up clearing debts
    - **Property 5: Settle-up clears all debts**
    - **Validates: Requirements 4.1, 4.2, 4.4**
  - [x]* 2.7 Write property test for settle-up transfer bound
    - **Property 6: Settle-up is minimal-bounded**
    - **Validates: Requirements 4.3, 4.5**
  - [x]* 2.8 Write property test for money formatting round-trip
    - **Property 7: Formatting round-trips**
    - **Validates: Requirements 5.4**

- [x] 3. Implement SQLite store
  - Groups, members, expenses, participants; validation of members and amounts
  - _Requirements: 1.1–1.4, 2.1, 2.3, 2.4, 2.5_

- [x] 4. Implement REST API and web UI
  - [x] 4.1 FastAPI routes per design table with 404/422 mapping
    - _Requirements: 5.1, 1.4, 2.3, 2.4_
  - [x] 4.2 One-page web UI at `/`
    - _Requirements: 5.2, 5.4_
  - [x]* 4.3 API example tests
    - _Requirements: 1.1–1.4, 2.1–2.5, 3.1, 4.1_

- [x] 5. Implement MCP server
  - [x] 5.1 Tools over stdio sharing the same DB
    - _Requirements: 5.3_
  - [x]* 5.2 MCP in-process smoke test
    - _Requirements: 5.3_

- [x] 6. Checkpoint - all tests pass (`uv run pytest -q`)

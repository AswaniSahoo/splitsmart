---
name: run-splitsmart
description: Use when the user wants to start the SplitSmart web app or API locally, or check that SplitSmart is installed correctly.
---

# Run SplitSmart locally

## Step 1: Check prerequisites
- `uv --version` must work. Install from https://docs.astral.sh/uv/ if missing.

## Step 2: Start the web app
```bash
uvx --from git+https://github.com/AswaniSahoo/splitsmart splitsmart
```
Open http://127.0.0.1:8000. The app binds to localhost only and has **no authentication** — do not expose it publicly.

## Step 3: Verify
Run `scripts/check.sh` from this skill folder; it calls `/api/groups` and prints `OK` if the server responds.

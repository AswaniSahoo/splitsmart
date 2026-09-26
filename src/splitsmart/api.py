"""FastAPI app: thin HTTP layer over store + ledger."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from splitsmart.ledger import compute_balances, format_cents, settle_up
from splitsmart.store import Store

STATIC = Path(__file__).parent / "static"


class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    members: list[str] = Field(min_length=1, max_length=50)


class MemberIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class ExpenseIn(BaseModel):
    description: str = Field(min_length=1, max_length=60)
    amount_cents: int = Field(gt=0, le=10**12)
    payer: str
    participants: list[str] = Field(min_length=1, max_length=50)


def create_app(store: Store | None = None) -> FastAPI:
    app = FastAPI(title="SplitSmart", version="0.1.0")
    app.state.store = store or Store()

    def db() -> Store:
        return app.state.store

    def call(fn, *args: Any) -> Any:
        try:
            return fn(*args)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc).strip("'\"")) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.post("/api/groups", status_code=201)
    def create_group(body: GroupIn) -> dict[str, Any]:
        return call(db().create_group, body.name, body.members)

    @app.get("/api/groups")
    def list_groups() -> list[dict[str, Any]]:
        return db().list_groups()

    @app.get("/api/groups/{group_id}")
    def get_group(group_id: int) -> dict[str, Any]:
        return call(db().get_group, group_id)

    @app.post("/api/groups/{group_id}/members", status_code=201)
    def add_member(group_id: int, body: MemberIn) -> dict[str, Any]:
        return call(db().add_member, group_id, body.name)

    @app.post("/api/groups/{group_id}/expenses", status_code=201)
    def add_expense(group_id: int, body: ExpenseIn) -> dict[str, Any]:
        return call(
            db().add_expense,
            group_id,
            body.description,
            body.amount_cents,
            body.payer,
            body.participants,
        )

    @app.delete("/api/groups/{group_id}/expenses/{expense_id}", status_code=204)
    def delete_expense(group_id: int, expense_id: int) -> None:
        call(db().delete_expense, group_id, expense_id)

    @app.get("/api/groups/{group_id}/balances")
    def balances(group_id: int) -> list[dict[str, Any]]:
        bal = call(lambda: compute_balances(db().members(group_id), db().ledger_expenses(group_id)))
        return [{"member": m, "balance_cents": b, "display": format_cents(b)} for m, b in bal.items()]

    @app.get("/api/groups/{group_id}/settle")
    def settle(group_id: int) -> list[dict[str, Any]]:
        bal = call(lambda: compute_balances(db().members(group_id), db().ledger_expenses(group_id)))
        return [
            {
                "from": t.from_member,
                "to": t.to_member,
                "amount_cents": t.amount_cents,
                "display": format_cents(t.amount_cents),
            }
            for t in settle_up(bal)
        ]

    return app

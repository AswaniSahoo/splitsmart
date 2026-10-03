import pytest
from fastapi.testclient import TestClient

from splitsmart.api import create_app
from splitsmart.store import Store


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(Store(str(tmp_path / "test.db"))))


def make_group(client, members=("Asha", "Ravi", "Meera")):
    r = client.post("/api/groups", json={"name": "Goa trip", "members": list(members)})
    assert r.status_code == 201
    return r.json()["id"]


def test_index_served(client):
    r = client.get("/")
    assert r.status_code == 200 and "SplitSmart" in r.text


def test_create_and_get_group(client):
    gid = make_group(client)
    g = client.get(f"/api/groups/{gid}").json()
    assert g["members"] == ["Asha", "Ravi", "Meera"] and g["expenses"] == []


def test_duplicate_members_rejected(client):
    r = client.post("/api/groups", json={"name": "x", "members": ["A", "A"]})
    assert r.status_code == 422


def test_unknown_group_404(client):
    assert client.get("/api/groups/999").status_code == 404
    assert client.get("/api/groups/999/balances").status_code == 404


def test_expense_balances_and_settle(client):
    gid = make_group(client)
    r = client.post(
        f"/api/groups/{gid}/expenses",
        json={
            "description": "Dinner",
            "amount_cents": 10000,
            "payer": "Asha",
            "participants": ["Asha", "Ravi", "Meera"],
        },
    )
    assert r.status_code == 201
    bal = {b["member"]: b["balance_cents"] for b in client.get(f"/api/groups/{gid}/balances").json()}
    # 10000 / 3 -> shares [3334, 3333, 3333]
    assert bal == {"Asha": 6666, "Ravi": -3333, "Meera": -3333}
    plan = client.get(f"/api/groups/{gid}/settle").json()
    assert sorted((t["from"], t["to"], t["amount_cents"]) for t in plan) == [
        ("Meera", "Asha", 3333),
        ("Ravi", "Asha", 3333),
    ]


@pytest.mark.parametrize("amount", [0, -5])
def test_non_positive_amount_rejected(client, amount):
    gid = make_group(client)
    r = client.post(
        f"/api/groups/{gid}/expenses",
        json={"description": "x", "amount_cents": amount, "payer": "Asha", "participants": ["Asha"]},
    )
    assert r.status_code == 422


def test_unknown_payer_rejected(client):
    gid = make_group(client)
    r = client.post(
        f"/api/groups/{gid}/expenses",
        json={"description": "x", "amount_cents": 100, "payer": "Zed", "participants": ["Asha"]},
    )
    assert r.status_code == 422 and "Zed" in r.json()["detail"]


def test_unknown_participant_rejected(client):
    gid = make_group(client)
    r = client.post(
        f"/api/groups/{gid}/expenses",
        json={"description": "x", "amount_cents": 100, "payer": "Asha", "participants": ["Asha", "Zed"]},
    )
    assert r.status_code == 422 and "Zed" in r.json()["detail"]


def test_add_member_and_delete_expense(client):
    gid = make_group(client, ["Asha", "Ravi"])
    r = client.post(f"/api/groups/{gid}/members", json={"name": "Kiran"})
    assert r.status_code == 201
    bal = {b["member"]: b["balance_cents"] for b in client.get(f"/api/groups/{gid}/balances").json()}
    assert bal["Kiran"] == 0
    eid = client.post(
        f"/api/groups/{gid}/expenses",
        json={
            "description": "Cab",
            "amount_cents": 900,
            "payer": "Ravi",
            "participants": ["Asha", "Ravi", "Kiran"],
        },
    ).json()["id"]
    assert client.delete(f"/api/groups/{gid}/expenses/{eid}").status_code == 204
    bal = client.get(f"/api/groups/{gid}/balances").json()
    assert all(b["balance_cents"] == 0 for b in bal)
    assert client.get(f"/api/groups/{gid}/settle").json() == []
    assert client.delete(f"/api/groups/{gid}/expenses/{eid}").status_code == 404

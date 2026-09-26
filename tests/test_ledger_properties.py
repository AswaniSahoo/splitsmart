"""Property-based tests for ledger.py (Correctness Properties 1-7 in design.md)."""

from collections import Counter
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from splitsmart.ledger import Expense, compute_balances, format_cents, settle_up, split_equal

NAMES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=6)
members_st = st.lists(NAMES, min_size=1, max_size=8, unique=True)
amount_st = st.integers(min_value=1, max_value=10**9)


@st.composite
def group_with_expenses(draw):
    members = draw(members_st)
    expenses = draw(
        st.lists(
            st.builds(
                lambda amt, payer, parts, d: Expense(d, amt, payer, tuple(parts)),
                amount_st,
                st.sampled_from(members),
                st.lists(st.sampled_from(members), min_size=1, unique=True),
                NAMES,
            ),
            max_size=25,
        )
    )
    return members, expenses


@st.composite
def zero_sum_balances(draw):
    members = draw(members_st)
    values = [draw(st.integers(-(10**9), 10**9)) for _ in members[:-1]]
    values.append(-sum(values))
    return dict(zip(members, values, strict=True))


# Feature: expense-splitter, Property 1: Split conserves money
@settings(max_examples=300)
@given(amount_st, members_st)
def test_split_conserves_money(amount, participants):
    shares = split_equal(amount, participants)
    assert sum(shares.values()) == amount
    assert max(shares.values()) - min(shares.values()) <= 1
    assert list(shares) == participants


# Feature: expense-splitter, Property 2: Balances sum to zero
@settings(max_examples=300)
@given(group_with_expenses())
def test_balances_sum_to_zero(data):
    members, expenses = data
    assert sum(compute_balances(members, expenses).values()) == 0


# Feature: expense-splitter, Property 3: Balances are order-independent
@settings(max_examples=200)
@given(group_with_expenses(), st.randoms(use_true_random=False))
def test_balances_order_independent(data, rnd):
    members, expenses = data
    shuffled = list(expenses)
    rnd.shuffle(shuffled)
    assert compute_balances(members, expenses) == compute_balances(members, shuffled)


# Feature: expense-splitter, Property 4: Deleting an expense is a perfect undo
@settings(max_examples=200)
@given(group_with_expenses(), st.data())
def test_delete_is_perfect_undo(data, draw):
    members, expenses = data
    extra = draw.draw(
        st.builds(
            lambda amt, payer, parts: Expense("extra", amt, payer, tuple(parts)),
            amount_st,
            st.sampled_from(members),
            st.lists(st.sampled_from(members), min_size=1, unique=True),
        )
    )
    idx = draw.draw(st.integers(0, len(expenses)))
    with_extra = expenses[:idx] + [extra] + expenses[idx:]
    removed = with_extra[:idx] + with_extra[idx + 1 :]
    assert compute_balances(members, removed) == compute_balances(members, expenses)


# Feature: expense-splitter, Property 5: Settle-up clears all debts
@settings(max_examples=300)
@given(zero_sum_balances())
def test_settle_up_clears_all_debts(balances):
    remaining = Counter(balances)
    for t in settle_up(balances):
        assert t.amount_cents > 0
        assert balances[t.from_member] < 0 < balances[t.to_member]
        remaining[t.from_member] += t.amount_cents
        remaining[t.to_member] -= t.amount_cents
    assert all(v == 0 for v in remaining.values())


# Feature: expense-splitter, Property 6: Settle-up is minimal-bounded
@settings(max_examples=300)
@given(zero_sum_balances())
def test_settle_up_transfer_bound(balances):
    nonzero = sum(1 for v in balances.values() if v != 0)
    plan = settle_up(balances)
    assert len(plan) <= max(nonzero - 1, 0)
    if nonzero == 0:
        assert plan == []


# Feature: expense-splitter, Property 7: Formatting round-trips
@settings(max_examples=500)
@given(st.integers(-(10**12), 10**12))
def test_format_round_trip(cents):
    assert Decimal(format_cents(cents)) * 100 == cents

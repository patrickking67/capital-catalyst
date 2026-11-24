from decimal import Decimal

import pytest

import ledger
from models import User, db


def make_user(username="alex"):
    user = User(username=username)
    user.set_password("correct horse battery")
    db.session.add(user)
    db.session.commit()
    return user


def test_balances_sum_per_account_and_sort(app):
    user = make_user()
    ledger.add_transaction(user, "Savings", "100.10")
    ledger.add_transaction(user, "Checking", "50.00")
    ledger.add_transaction(user, "Savings", "-20.05")
    assert ledger.account_balances(user) == [
        ("Checking", Decimal("50.00")),
        ("Savings", Decimal("80.05")),
    ]


def test_cents_do_not_drift(app):
    user = make_user()
    for _ in range(10):
        ledger.add_transaction(user, "Checking", "0.10")
    assert ledger.account_balances(user) == [("Checking", Decimal("1.00"))]


def test_balances_are_per_user(app):
    alex, sam = make_user("alex"), make_user("sam")
    ledger.add_transaction(alex, "Checking", "10.00")
    ledger.add_transaction(sam, "Checking", "99.00")
    assert ledger.account_balances(alex) == [("Checking", Decimal("10.00"))]
    assert ledger.account_balances(make_user("nobody")) == []


def test_holdings_sum_lots_per_asset(app):
    user = make_user()
    ledger.add_holding(user, "Index fund", "1.5")
    ledger.add_holding(user, "Index fund", "0.25")
    ledger.add_holding(user, "Bond fund", "3")
    assert ledger.holdings(user) == [("Bond fund", Decimal("3")), ("Index fund", Decimal("1.75"))]


def test_invalid_entries_are_rejected_and_not_saved(app):
    user = make_user()
    with pytest.raises(ValueError):
        ledger.add_transaction(user, "Checking", "1.005")
    with pytest.raises(ValueError):
        ledger.add_holding(user, "Fund", "-1")
    assert ledger.account_balances(user) == []
    assert ledger.holdings(user) == []


def test_get_user(app):
    make_user("alex")
    assert ledger.get_user("alex").username == "alex"
    assert ledger.get_user("missing") is None

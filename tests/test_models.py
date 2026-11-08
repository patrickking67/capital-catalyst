from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from models import Investment, Transaction, User, db


def make_user(username="alex"):
    user = User(username=username)
    user.set_password("correct horse battery")
    db.session.add(user)
    db.session.commit()
    return user


def test_password_is_hashed_and_checked(app):
    user = make_user()
    assert user.password_hash != "correct horse battery"
    assert user.check_password("correct horse battery")
    assert not user.check_password("wrong password")
    assert not user.check_password(None)


def test_full_scrypt_hash_fits_column(app):
    user = make_user()
    stored = db.session.get(User, user.id)
    assert stored.check_password("correct horse battery")


def test_user_without_password_never_matches(app):
    assert not User(username="nopass").check_password("anything")


def test_short_password_is_rejected(app):
    with pytest.raises(ValueError, match="at least 8"):
        User(username="alex").set_password("short")


@pytest.mark.parametrize("username", ["", "ab", "has space", "x" * 65, None, "semi;colon"])
def test_invalid_username_is_rejected(app, username):
    with pytest.raises(ValueError, match="username"):
        User(username=username)


def test_username_is_unique(app):
    make_user("sam")
    db.session.add(User(username="sam"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_transaction_stores_exact_amount(app):
    user = make_user()
    db.session.add(Transaction(account="  Checking ", amount="0.10", user=user))
    db.session.add(Transaction(account="Checking", amount=Decimal("0.20"), user=user))
    db.session.commit()
    total = sum(t.amount for t in user.transactions)
    assert total == Decimal("0.30")
    assert user.transactions[0].account == "Checking"


def test_transaction_allows_negative_amounts(app):
    assert Transaction(account="Checking", amount=-25).amount == Decimal("-25")


@pytest.mark.parametrize(
    "amount", ["abc", None, True, float("nan"), float("inf"), "Infinity", "1.005"]
)
def test_invalid_amount_is_rejected(app, amount):
    with pytest.raises(ValueError, match="amount"):
        Transaction(account="Checking", amount=amount)


@pytest.mark.parametrize("account", ["", "   ", None, "x" * 121])
def test_invalid_account_is_rejected(app, account):
    with pytest.raises(ValueError, match="account"):
        Transaction(account=account, amount=1)


def test_transaction_requires_user(app):
    db.session.add(Transaction(account="Checking", amount=1))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_investment_round_trip(app):
    user = make_user()
    db.session.add(Investment(asset="Index fund", quantity="1.5", user=user))
    db.session.commit()
    holding = user.investments[0]
    assert holding.asset == "Index fund"
    assert holding.quantity == Decimal("1.5")
    assert holding.user is user


@pytest.mark.parametrize("quantity", [0, -1, "zero", None, "0.000000001"])
def test_invalid_quantity_is_rejected(app, quantity):
    with pytest.raises(ValueError, match="quantity"):
        Investment(asset="Index fund", quantity=quantity)


@pytest.mark.parametrize("asset", ["", None, "x" * 121])
def test_invalid_asset_is_rejected(app, asset):
    with pytest.raises(ValueError, match="asset"):
        Investment(asset=asset, quantity=1)

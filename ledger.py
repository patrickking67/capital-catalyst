"""Read-only summaries of what a user has recorded. No prices, no valuation, no advice.

Everything here adds up numbers the user entered. Amounts stay Decimal.
"""

from decimal import Decimal

from sqlalchemy import func

from models import Investment, Transaction, User, db


def get_user(username):
    """Return the user with this username, or None."""
    return db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()


def account_balances(user):
    """Return [(account, balance)] sorted by account name, summing each account's transactions."""
    rows = db.session.execute(
        db.select(Transaction.account, func.sum(Transaction.amount))
        .filter(Transaction.user_id == user.id)
        .group_by(Transaction.account)
        .order_by(Transaction.account)
    ).all()
    return [(account, Decimal(total)) for account, total in rows]


def holdings(user):
    """Return [(asset, quantity)] sorted by asset name, summing each asset's recorded lots."""
    rows = db.session.execute(
        db.select(Investment.asset, func.sum(Investment.quantity))
        .filter(Investment.user_id == user.id)
        .group_by(Investment.asset)
        .order_by(Investment.asset)
    ).all()
    return [(asset, Decimal(total)) for asset, total in rows]


def add_transaction(user, account, amount):
    """Record a transaction. Validation happens in the model and raises ValueError."""
    transaction = Transaction(user_id=user.id, account=account, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    return transaction


def add_holding(user, asset, quantity):
    """Record a holding lot. Validation happens in the model and raises ValueError."""
    investment = Investment(user_id=user.id, asset=asset, quantity=quantity)
    db.session.add(investment)
    db.session.commit()
    return investment

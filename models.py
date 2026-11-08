"""Database models: users, account transactions and investment holdings."""

import math
import re
from decimal import Decimal, InvalidOperation

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,64}$")
MAX_NAME_LENGTH = 120
MIN_PASSWORD_LENGTH = 8


def _clean_name(field, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    value = value.strip()
    if len(value) > MAX_NAME_LENGTH:
        raise ValueError(f"{field} must be {MAX_NAME_LENGTH} characters or fewer")
    return value


def _to_decimal(field, value):
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a number")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{field} must be a number") from None
    if not number.is_finite():
        raise ValueError(f"{field} must be a finite number")
    return number


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    # Werkzeug's default scrypt hashes are longer than 128 characters.
    password_hash = db.Column(db.String(255))

    transactions = db.relationship("Transaction", back_populates="user")
    investments = db.relationship("Investment", back_populates="user")

    @validates("username")
    def validate_username(self, key, value):
        if not isinstance(value, str) or not USERNAME_PATTERN.match(value):
            raise ValueError(
                "username must be 3 to 64 characters: letters, digits, '.', '_' or '-'"
            )
        return value

    def set_password(self, password):
        if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"password must be at least {MIN_PASSWORD_LENGTH} characters")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash or not isinstance(password, str):
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    # Numeric, not Float, so cents do not drift through binary rounding.
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="transactions")

    @validates("account")
    def validate_account(self, key, value):
        return _clean_name("account", value)

    @validates("amount")
    def validate_amount(self, key, value):
        amount = _to_decimal("amount", value)
        if amount != amount.quantize(Decimal("0.01")):
            raise ValueError("amount must have at most 2 decimal places")
        return amount


class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(MAX_NAME_LENGTH), nullable=False)
    quantity = db.Column(db.Numeric(20, 8), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    user = db.relationship("User", back_populates="investments")

    @validates("asset")
    def validate_asset(self, key, value):
        return _clean_name("asset", value)

    @validates("quantity")
    def validate_quantity(self, key, value):
        quantity = _to_decimal("quantity", value)
        if quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        if quantity != quantity.quantize(Decimal("0.00000001")):
            raise ValueError("quantity must have at most 8 decimal places")
        return quantity

"""Capital Catalyst Flask application.

Run with ``flask --app app run``. Flask finds ``create_app`` on its own.
"""

import os

import click
from flask import Flask, render_template

import ledger
from models import User, db

DEFAULT_DATABASE_URL = "sqlite:///capital_catalyst.db"


def load_config(overrides=None):
    """Build the app config from environment variables plus optional overrides."""
    config = {
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "SQLALCHEMY_DATABASE_URI": os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    if overrides:
        config.update(overrides)
    if not config.get("SECRET_KEY") and not config.get("TESTING"):
        raise RuntimeError(
            "SECRET_KEY is not set. Export SECRET_KEY before starting the app "
            "(scripts/dev.sh sets a fake one for local development)."
        )
    return config


def create_app(config=None):
    """Application factory."""
    app = Flask(__name__)
    app.config.update(load_config(config))
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    register_routes(app)
    register_error_handlers(app)
    register_security_headers(app)
    register_cli(app)
    return app


def register_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/accounts")
    def accounts():
        return render_template("accounts.html")

    @app.route("/investments")
    def investments():
        return render_template("investments.html")

    @app.route("/contact")
    def contact():
        return render_template("contact.html")


ERROR_PAGES = {
    404: ("Page not found", "There is no page at this address. Check the link or start again."),
    405: ("Method not allowed", "This page does not accept that kind of request."),
    500: (
        "Server error",
        "Something failed on the server. Try again. If it keeps happening, open an issue.",
    ),
}


def register_error_handlers(app):
    def render_error(code):
        heading, message = ERROR_PAGES[code]
        page = render_template("error.html", code=code, heading=heading, message=message)
        return page, code

    for code in ERROR_PAGES:
        app.register_error_handler(code, lambda error, code=code: render_error(code))


SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' data:; base-uri 'self'; "
        "form-action 'self'; frame-ancestors 'none'; object-src 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


def register_security_headers(app):
    @app.after_request
    def set_security_headers(response):
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        return response


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create the database tables if they do not exist."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.password_option(confirmation_prompt=True)
    def create_user(username, password):
        """Create a user. The password is prompted for and stored as a hash."""
        if ledger.get_user(username):
            raise click.ClickException(f"User {username!r} already exists.")
        user = User()
        try:
            user.username = username
            user.set_password(password)
        except ValueError as error:
            raise click.ClickException(str(error)) from None
        db.session.add(user)
        db.session.commit()
        click.echo(f"Created user {username}.")

    @app.cli.command("add-transaction", context_settings={"ignore_unknown_options": True})
    @click.argument("username")
    @click.argument("account")
    @click.argument("amount")
    def add_transaction(username, account, amount):
        """Record AMOUNT (negative for money out) against ACCOUNT for USERNAME."""
        user = _require_user(username)
        try:
            ledger.add_transaction(user, account, amount)
        except ValueError as error:
            db.session.rollback()
            raise click.ClickException(str(error)) from None
        click.echo("Transaction recorded.")

    @app.cli.command("add-holding")
    @click.argument("username")
    @click.argument("asset")
    @click.argument("quantity")
    def add_holding(username, asset, quantity):
        """Record QUANTITY of ASSET that USERNAME holds. This does not value it."""
        user = _require_user(username)
        try:
            ledger.add_holding(user, asset, quantity)
        except ValueError as error:
            db.session.rollback()
            raise click.ClickException(str(error)) from None
        click.echo("Holding recorded.")

    @app.cli.command("balances")
    @click.argument("username")
    def balances(username):
        """Print each account's balance: the sum of the amounts you recorded."""
        rows = ledger.account_balances(_require_user(username))
        if not rows:
            click.echo("No transactions recorded.")
        for account, total in rows:
            click.echo(f"{account}: {total:,.2f}")

    @app.cli.command("holdings")
    @click.argument("username")
    def holdings(username):
        """Print each asset and the total quantity you recorded. No prices, no values."""
        rows = ledger.holdings(_require_user(username))
        if not rows:
            click.echo("No holdings recorded.")
        for asset, quantity in rows:
            click.echo(f"{asset}: {quantity.normalize():f}")


def _require_user(username):
    user = ledger.get_user(username)
    if user is None:
        raise click.ClickException(f"No user named {username!r}. Create one with create-user.")
    return user

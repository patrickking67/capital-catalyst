"""Capital Catalyst Flask application.

Run with ``flask --app app run``. Flask finds ``create_app`` on its own.
"""

import os

import click
from flask import Flask, render_template

from models import db

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

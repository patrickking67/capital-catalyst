# Capital Catalyst

[![CI](https://github.com/patrickking67/capital-catalyst/actions/workflows/ci.yml/badge.svg)](https://github.com/patrickking67/capital-catalyst/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An early Flask app for keeping track of your own accounts and investments. Version 1.0 is a scaffold: the pages and the data model exist, and the screens that use them do not yet.

There is no live deployment.

> Not financial advice. Capital Catalyst does not connect to banks or brokers, does not fetch prices and does not make recommendations. Anything it shows is data you entered yourself.

## Features

What works today:

- Four pages: Home, Accounts, Investments and Contact, sharing one layout with light and dark color schemes.
- Data model (Flask-SQLAlchemy) for users, transactions and investment holdings:
  - passwords stored as Werkzeug hashes, never in plain text
  - amounts and quantities stored as exact decimals, not floats
  - validation for usernames, account and asset names, amounts and quantities
- `flask init-db` command to create the tables.
- 404, 405 and 500 error pages and basic security headers.

Not built yet: sign in, recording transactions, recording holdings, and any page that reads from the database. The Accounts and Investments pages show empty tables that say so.

## Quickstart

Needs Python 3.11 or newer.

```sh
git clone git@github.com:patrickking67/capital-catalyst.git
cd capital-catalyst
scripts/setup.sh     # creates .venv and installs requirements-dev.txt
scripts/dev.sh       # http://127.0.0.1:4108
```

`scripts/dev.sh` sets a fake development `SECRET_KEY`. To create the database tables:

```sh
SECRET_KEY=dev-only-not-a-real-secret .venv/bin/flask --app app init-db
```

## Configuration

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `SECRET_KEY` | Yes | none | Flask secret key. The app refuses to start without it. |
| `DATABASE_URL` | No | `sqlite:///capital_catalyst.db` | SQLAlchemy URL. Relative SQLite paths live in `instance/`. |

## Architecture

| Path | What it is |
| --- | --- |
| `app.py` | App factory `create_app()`, config from the environment, routes, error pages, security headers, `init-db` command |
| `models.py` | `User`, `Transaction`, `Investment` models and their validation |
| `templates/` | `base.html` layout, one template per page, `error.html` |
| `static/` | `css/main.css` and `favicon.svg` |
| `tests/` | pytest suite for config, models and routes |
| `scripts/` | `setup.sh`, `dev.sh`, `check.sh` |

## Tests

```sh
scripts/check.sh
```

Runs `ruff check`, `ruff format --check` and `pytest`. CI runs the same script on Python 3.11 to 3.14.

## Deploy

Not deployed. To run it behind a WSGI server, set `SECRET_KEY` (and `DATABASE_URL` if not using SQLite) and point the server at `app:create_app()`. No WSGI server is pinned in `requirements.txt`.

## License

[MIT](LICENSE)

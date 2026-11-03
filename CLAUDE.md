# Capital Catalyst

Early Flask scaffold for a personal finance app: four routes (home, accounts, investments, contact), a shared `base.html` layout, and SQLAlchemy models for users, transactions and investments. Most templates and `static/js/main.js` are still empty, and the models are not wired to a database yet.

## Commands

| Task | Command | Notes |
| --- | --- | --- |
| Syntax check | `python3 -m py_compile app.py models.py` | The only check that runs today |
| Dev server | `flask --app app run` | Flask default port 5000. Needs `flask` and `flask-sqlalchemy`, which are not pinned anywhere (see below) |

No tests, linter or build.

## Layout

| Path | What it is |
| --- | --- |
| `app.py` | Flask app and routes. Imports `db` from `models.py` but never calls `db.init_app` or sets a database URI |
| `models.py` | `User`, `Transaction`, `Investment` (Flask-SQLAlchemy) |
| `templates/` | `base.html` (nav + content block) and one template per route |
| `static/` | `css/main.css`, `js/main.js` |
| `venv/` | A committed Python 3.9 virtualenv. It does not contain Flask or Flask-SQLAlchemy and points at a framework Python 3.9 path, so it is not usable as is |

## Known gaps

- `requirements.txt` is empty and there is no `.gitignore`, so `venv/` and `__pycache__/` get committed. Ask before changing dependencies or removing `venv/`.
- Passwords are meant to be stored as `password_hash`; never store or log a plain password.

## Verify a change

Run the syntax check. For page changes, install Flask and Flask-SQLAlchemy in a fresh virtualenv outside `venv/`, run the dev server and load each route.

## Deploy risk

No deploy config or CI. Nothing ships automatically.

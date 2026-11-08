# AGENTS.md

Guide for coding agents working on Capital Catalyst.

## What it is

A small Flask scaffold for a personal finance app. Four static pages, a Flask-SQLAlchemy data model (users, transactions, investments) that no page reads yet, and no sign in. Not financial advice: never add copy or features that present output as a recommendation.

## Stack

- Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, SQLAlchemy 2.1, Jinja templates, plain CSS. No JavaScript.
- SQLite by default (`instance/capital_catalyst.db`).
- Tools: pytest, ruff. All versions pinned in `requirements.txt` and `requirements-dev.txt`.

## Layout

| Path | Purpose |
| --- | --- |
| `app.py` | `create_app()` factory, `load_config()`, routes, error handlers, security headers, `init-db` CLI |
| `models.py` | `db`, `User`, `Transaction`, `Investment`, validators |
| `templates/` | `base.html` plus one template per page and `error.html` |
| `static/css/main.css` | All styles (ledger look, light and dark) |
| `tests/` | `conftest.py` fixtures, `test_config.py`, `test_models.py`, `test_routes.py` |
| `scripts/` | `setup.sh`, `dev.sh`, `check.sh` |
| `.claude/launch.json` | Preview config: runs `scripts/dev.sh` on port 4108 |

## Commands

| Task | Command |
| --- | --- |
| Install | `scripts/setup.sh` (creates `.venv`, installs `requirements-dev.txt`) |
| Check (lint, format, tests) | `scripts/check.sh` |
| Format | `.venv/bin/ruff format .` |
| Run / preview | `scripts/dev.sh` then open http://127.0.0.1:4108 |
| Create tables | `SECRET_KEY=dev-only-not-a-real-secret .venv/bin/flask --app app init-db` |

There is no build step.

## Conventions

- Keep the app factory. Do not create a module-level `app`; tests build their own with `create_app({...})`.
- Configuration comes from environment variables only. `SECRET_KEY` is required outside tests.
- Money is `Numeric` and `Decimal`, never `float`.
- Validate input in model `@validates` methods and at any new route boundary. Any new form needs CSRF protection.
- Templates extend `base.html`. Keep landmarks, the skip link, visible focus and WCAG AA contrast. Check 375px width.
- Every behaviour change gets a test. `pytest` treats warnings as errors.
- Conventional Commits, one logical change per commit, each passing `scripts/check.sh`.

## Safety

- Never commit secrets, real account data or personal financial details. Use obviously fake values in tests.
- Never commit `.venv/`, `venv/`, `instance/` or `*.db` (all gitignored).
- Do not add features that fetch prices, connect to financial institutions or give advice without the owner asking.

## Do not touch

- `LICENSE`.
- Pinned versions, unless the change is the point of the task. Rerun `scripts/check.sh` after any bump.

## Shipping

1. Branch from `main` (`feat/`, `fix/`, `docs/`, `chore/`).
2. Run `scripts/check.sh`; for template or CSS changes also run `scripts/dev.sh` and check each page.
3. Update `CHANGELOG.md` under `[Unreleased]`.
4. Open a PR against `main`. CI must pass. Nothing deploys automatically.

## Definition of done

`scripts/check.sh` passes, the changed pages load with status 200 in the preview, tests cover the change, and the CHANGELOG is updated.

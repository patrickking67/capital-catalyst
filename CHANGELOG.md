# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- App factory `create_app()` with configuration from `SECRET_KEY` and `DATABASE_URL`.
- `flask init-db` command to create the database tables.
- `User.set_password` and `User.check_password`.
- Validation for usernames, account and asset names, amounts and quantities.
- Page content for Home, Accounts, Investments and Contact, with a not-financial-advice note.
- New stylesheet with light and dark schemes, meta tags and an SVG favicon.
- 404, 405 and 500 error pages and security headers.
- pytest suite, ruff config and `scripts/check.sh`; `scripts/setup.sh` and `scripts/dev.sh`.
- GitHub Actions CI, Dependabot, CODEOWNERS, issue and PR templates.
- README rewrite, AGENTS.md, CLAUDE.md, CONTRIBUTING.md, SECURITY.md, llms.txt, MIT license.

### Changed

- Dependencies pinned for Python 3.11 and newer: Flask 3.1.3, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.8.
- Transaction amounts and investment quantities are stored as `Numeric`, not `Float`.
- `password_hash` widened to 255 characters so Werkzeug scrypt hashes fit.
- Transactions and investments now require a user.

### Fixed

- Every page rendered blank because the page templates were empty and did not extend the layout.
- The database was never initialised, so the models could not be used.

### Removed

- The committed `venv/` directory (now gitignored).
- The empty `static/js/main.js`.

## [1.0.0] - 2023-07-26

### Added

- Initial Flask scaffold: routes for Home, Accounts, Investments and Contact, a base layout, and `User`, `Transaction` and `Investment` models.

[Unreleased]: https://github.com/patrickking67/capital-catalyst/compare/83e020f...HEAD
[1.0.0]: https://github.com/patrickking67/capital-catalyst/commit/83e020f

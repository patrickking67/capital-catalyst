# Contributing

Thanks for helping. Capital Catalyst is a small personal project, so keep changes focused.

## Setup

Needs Python 3.11 or newer.

```sh
scripts/setup.sh   # creates .venv and installs requirements-dev.txt
scripts/check.sh   # ruff check, ruff format --check, pytest
scripts/dev.sh     # dev server on http://127.0.0.1:4108
```

## Branches

Branch from `main` and name the branch by type:

- `feat/<short-name>` for new behaviour
- `fix/<short-name>` for bug fixes
- `docs/<short-name>` for documentation
- `chore/<short-name>` for tooling, dependencies and housekeeping

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `chore:`, `build:`, `ci:`, `test:`, `refactor:`. One logical change per commit, and each commit should pass `scripts/check.sh`.

## Pull request checklist

- [ ] `scripts/check.sh` passes
- [ ] New or changed behaviour has tests
- [ ] Template or CSS changes checked in the browser, including a 375px wide screen
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] No secrets, real account data or personal financial details
- [ ] No copy or feature that presents output as financial advice

## Checks

CI runs `scripts/check.sh` on every push to `main` and every pull request, on Python 3.11 to 3.14. A PR needs a green run before merge.

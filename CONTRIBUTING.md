# Contributing to Postmarker

## Report bugs

Report bugs in the [issue tracker](https://github.com/Stranger6667/postmarker/issues). Please include:

- the steps that reproduce the problem;
- what you expected and what happened instead;
- Python, Postmarker and, if relevant, Django versions.

A failing test that demonstrates the problem is very welcome.

## Pull requests

1. Fork the repository and target the `master` branch.
2. Install the [prek](https://prek.j178.dev) hooks: `prek install -t pre-commit -t commit-msg`.
3. Run the tests with tox, for example `tox -e py314-django61`.
4. Add an entry under `Unreleased` in `CHANGELOG.md` for user-visible changes.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`fix: ...`, `feat: ...`); CI checks them.

## Recorded API responses

Tests replay recorded Postmark API responses with [pytest-recording](https://github.com/kiwicom/pytest-recording).
Cassettes live in the `cassettes/` directory next to each test module, one file per test.
To record new ones against a real Postmark server:

```
SERVER_TOKEN=... ACCOUNT_TOKEN=... tox -e record -- test/models/test_bounces.py
```

Token headers are replaced with placeholders, but response bodies are stored as they are: check them for real data before committing.

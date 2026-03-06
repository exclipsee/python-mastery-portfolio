# Contributing

Thanks for wanting to contribute! A few guidelines to make contributions smooth.

- Branch from `main` and use a descriptive branch name, e.g. `fix/xyz` or `feature/abc`.
- Run tests locally before opening a PR:

```powershell
python -m pip install -e .[dev]
python -m pytest -q
```

- Install pre-commit hooks and run them before committing:

```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

- Create a PR and include a short description, testing steps, and link any issues.
- Maintain small, focused PRs when possible.


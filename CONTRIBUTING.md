# Contributing

Thanks for considering a contribution. Keep changes small and focused.

Guidelines
- Follow the existing style (Black + Ruff) and type hints where practical.
- Add or update tests under `tests/` for any behaviour you change.
- Run the test suite locally: `pytest -q`.
- Keep public APIs stable; prefer additive changes.

Code style
- Format with `black .` and lint with `ruff` before committing.

Pull requests
- Open a PR from a topic branch and reference the issue (if any).
- Use a clear title and short description of the change and reasoning.
- Include screenshots / sample output if relevant.
- Tag reviewers and request changes when ready.

Development setup

```bash
python -m pip install -e '.[dev]'
```

Reach out
If you need help, open an issue describing the problem and someone will respond.

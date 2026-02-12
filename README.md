# python-mastery-portfolio

- ![CI](https://github.com/exclipsee/python-mastery-portfolio/actions/workflows/ci.yml/badge.svg?branch=main)  ![Codecov](https://codecov.io/gh/exclipsee/python-mastery-portfolio/branch/main/graph/badge.svg)

Hey — I'm a freelance dev. This repo is a grab-bag of small, useful Python
tools and demos I use in interviews and toy projects. It's practical, simple,
and ready to play with.

What you'll find:

- Small utilities (VIN tools, algorithms)
- Tiny ML helpers (train/predict demo)
- A simple FastAPI demo and a CLI
- Tests and a couple of tiny benchmarks

## Quick start

Install in editable mode (dev extras):

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Run tests:

```bash
pytest -q
```

CLI examples (after installing the package):

```bash
# compute Fibonacci number
pm-portfolio fib 10

# compute gcd
pm-portfolio gcd 54 24

# validate a VIN
pm-portfolio vin-validate 1HGCM82633A004352

# train a tiny linear model and save it
pm-portfolio ml-train --y 3 5 --x "1,2" "2,3" --save model.joblib
```

Run the API locally with uvicorn:

```bash
uvicorn python_mastery_portfolio.api:app --reload --port 8000
```

HTTP examples:

```bash
# Fibonacci (GET)
curl http://127.0.0.1:8000/fib/10

# VIN validation (POST)
curl -s -X POST http://127.0.0.1:8000/vin/validate -H 'Content-Type: application/json' -d '{"vin":"1HGCM82633A004352"}'
```
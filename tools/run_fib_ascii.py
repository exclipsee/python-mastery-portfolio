from typer.testing import CliRunner
from python_mastery_portfolio.cli import app

if __name__ == "__main__":
    runner = CliRunner()
    res = runner.invoke(app, ["fib", "6", "--ascii"])
    print(res.stdout)
    if res.exit_code != 0:
        raise SystemExit(res.exit_code)


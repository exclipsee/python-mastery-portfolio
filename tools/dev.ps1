param(
    [string]$Task = 'help'
)

switch ($Task.ToLower()) {
    'help' {
        Write-Host "Tasks: test, format, precommit-install, bump-patch"
    }
    'test' {
        .\run_tests.ps1
    }
    'format' {
        python -m black .
        python -m isort .
    }
    'precommit-install' {
        pip install pre-commit
        pre-commit install
    }
    'bump-patch' {
        python tools/bump_version.py patch
    }
    default {
        Write-Host "Unknown task: $Task"
    }
}


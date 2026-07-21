# Python Bots

This directory contains bots written in Python.

## Linting & Formatting

Python bots in this directory are checked with:

- **Flake8** — linting (PEP 8 compliance, code style errors)
- **Black** — code formatting

### Running checks locally

```bash
# Install tools
pip install flake8 black

# Lint
flake8 python_bots/ --max-line-length=120

# Check formatting
black --check python_bots/

# Auto-format
black python_bots/
```

## Adding a New Python Bot

1. Create a subdirectory: `python_bots/<bot_name>/`
2. Add your Python source files (`.py`)
3. Ensure all files pass Flake8 and Black checks before submitting a PR

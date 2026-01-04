## Setup (uv + venv)

This project uses `uv` to manage the virtual environment and dependencies.

Prerequisites
1) Install `uv` (see Astral uv docs).
2) Have a supported Python installed (or let uv fetch one).

First-time setup (from repo root)
Windows (PowerShell):
1) Create a venv:
   uv venv --python 3.12
2) Install dependencies (and install this project in editable mode):
   uv sync

macOS / Linux (bash/zsh):
1) Create a venv:
   uv venv --python 3.13
2) Install dependencies:
   uv sync

Notes
- `uv sync` installs the project in editable mode by default (changes in `src/` are reflected immediately). This requires a valid `[build-system]` in `pyproject.toml`.
- You do NOT need to activate the venv if you use `uv run ...`.

## Running commands

- uv run scanner-app
- uv run scanner-api
- uv run scanner-ingest --symbol aapl.us
- uv run scanner-scan --symbol aapl.us

Optional: activate the venv (only if you want to run commands without `uv run`)
Windows:
  .venv\Scripts\activate
macOS/Linux:
  source .venv/bin/activate

## Troubleshooting

If `uv sync` doesn’t install the project:
- Check that `pyproject.toml` contains a `[build-system]` section (without it, uv won’t install the current project as a package).
- Then re-run:
  uv sync
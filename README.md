# Cash Flow Planner Desktop

An offline-first **cash-flow forecasting** and **scenario-planning** desktop app for individuals and small businesses. Define income and expense entries with a flexible date-pattern syntax; the app projects cash flows over time, computes running balance, and alerts you to the first deficit — with what-if scenarios to test changes before they affect your saved forecast.

- **Stack:** Python 3.12 · PySide6 (Qt 6) · QML · SQLite / SQLAlchemy · Alembic · Pydantic v2
- **Platforms:** macOS · Windows · Linux

## Quick Links

| Resource | Path |
|----------|------|
| System Design | [`docs/DESIGN.md`](docs/DESIGN.md) |
| Local Builds & Installers | [`docs/BUILD.md`](docs/BUILD.md) |
| Documentation Index | [`docs/README.md`](docs/README.md) |
| Agent / AI Guide | [`AGENTS.md`](AGENTS.md) |
| Issues | [GitHub Issues](https://github.com/sekurado/cash-flow-planner-app/issues) |
| Project Board | [Project #2](https://github.com/users/sekurado/projects/2) |
| Development History | [`docs/DEVELOPMENT_HISTORY.md`](docs/DEVELOPMENT_HISTORY.md) |

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the app
python main.py

# Run tests
pytest

# Lint + type-check
ruff check src && mypy --strict src
```

## Building installers

See [`docs/BUILD.md`](docs/BUILD.md) for one-command local builds (`.dmg`, `.exe`, `.AppImage`)
to share with others.

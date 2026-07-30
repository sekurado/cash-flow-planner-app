# Contributing

Thank you for your interest in **Cash Flow Planner Desktop**. This document explains how the
project is built and how to participate.

---

## How this project is developed

This repository follows a **human-directed, AI-assisted** workflow:

- **Human-led:** product direction, architecture, issue specs, UX decisions, and merge approval.
- **Agent-assisted:** most implementation is drafted by coding agents (e.g. Cursor) from those specs.
- **Human-reviewed:** the maintainer reviews the majority of changes before they land — architecture fit, edge cases, tests, and security-sensitive paths.

Agents do not merge on their own. Every change is expected to pass the same quality gates as
hand-written code: `ruff`, `mypy --strict`, and `pytest`.

If you are evaluating the pace or polish of the codebase — yes, agents accelerate implementation.
The design constraints, review bar, and accountability remain human.

For conventions agents must follow in this repo, see [`AGENTS.md`](AGENTS.md).

---

## Workflow

Active work is tracked on [GitHub Issues](https://github.com/sekurado/cash-flow-planner-app/issues).

| Step | What happens |
|------|----------------|
| Plan | A Story or Task issue is opened with acceptance criteria in the body. |
| Implement | An agent (or contributor) implements against the spec and project conventions. |
| Review | Changes are reviewed for correctness, architecture, and test coverage. |
| Verify | `ruff check`, `mypy --strict`, and `pytest` must pass. |
| Land | Commits reference the issue; completed tasks use `Closes #N` when appropriate. |

Completed Stories 1–30 are archived in [`docs/DEVELOPMENT_HISTORY.md`](docs/DEVELOPMENT_HISTORY.md).

---

## Getting started

```bash
# Clone and install
pip install -e ".[dev]"

# Run the app
python main.py

# Run tests
pytest

# Lint + type-check
ruff check src && mypy --strict src
```

See [`docs/DESIGN.md`](docs/DESIGN.md) for architecture and [`docs/BUILD.md`](docs/BUILD.md) for
installer builds.

---

## Pull requests

1. **Discuss first** for large changes — open or comment on an issue so scope is clear.
2. **Keep PRs focused** — one task or logical unit of work per PR when possible.
3. **Follow conventions** in [`AGENTS.md`](AGENTS.md) and [`.cursor/rules/`](.cursor/rules/).
4. **Add tests** for new domain logic; integration tests for new ViewModels.
5. **Update docs** when architecture or public behavior changes (`docs/DESIGN.md`, issue bodies).

---

## Architecture rules (summary)

- **Layer direction:** Presentation → Application → Business → Data. Never reverse.
- **Pure domain:** `src/domain/` has no Qt imports.
- **Repositories only** touch the database session.
- **ViewModels** catch exceptions in `@Slot` methods and surface them via the `error` property — never re-raise into QML.

Full detail is in [`docs/DESIGN.md`](docs/DESIGN.md) and [`AGENTS.md`](AGENTS.md).

---

## Questions

Open a [GitHub Issue](https://github.com/sekurado/cash-flow-planner-app/issues) for bugs,
feature ideas, or questions about contributing.

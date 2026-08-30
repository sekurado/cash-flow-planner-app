# Cash Flow Planner Desktop — Agent Guide

This file provides persistent context, conventions, and best practices for AI agents working on this codebase. Read it before making any changes.

---

## Project Overview

**Cash Flow Planner Desktop** is an offline cash-flow forecasting tool for individuals and small businesses. Users define income and expense entries using a flexible date-pattern syntax; the app projects those entries over a time horizon, computes a running balance, surfaces the first date a cash-flow deficit would occur, and supports what-if scenario planning without altering saved plans.

- Single Python process — PySide6 (Qt 6) with QML for UI
- All data stored locally in SQLite; no cloud dependency
- Distributed as a native binary for macOS, Windows, and Linux

**Key docs:**
- [`docs/DESIGN.md`](docs/DESIGN.md) — full system design, architecture, domain model, tech decisions
- [`docs/README.md`](docs/README.md) — documentation index
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — development workflow (human-directed, AI-assisted) and PR expectations

---

## Architecture Summary

```
Presentation  →  QML Views & Components
Application   →  ViewModels (QObject subclasses), Qt List Models
Business      →  SimulationEngine, DatePattern, CurrencyNormalizer (pure Python, no Qt)
Data          →  Repositories, SQLAlchemy Core, Alembic migrations
```

Strict one-direction dependency: higher layers depend on lower ones, never the reverse. Business logic must never import from Qt. ViewModels are the only bridge between Qt and pure Python.

---

## Tech Stack Best Practices

### Python / General

- Target **Python 3.12+**. Use `from __future__ import annotations` in all modules.
- Format with **`ruff format`**, lint with **`ruff check`**, type-check with **`mypy --strict`**. Fix all violations before committing.
- Prefer `pathlib.Path` over `os.path`. Use `datetime.date` (not `datetime.datetime`) for calendar dates unless time-of-day is required.
- No mutable default arguments. No bare `except:` — always catch a specific exception class.

### PySide6 / Qt

- All UI updates must happen on the **main thread**. Worker threads communicate back via signals (Qt auto-queues cross-thread signal/slot calls).
- Expose state to QML as `Q_PROPERTY` with `NOTIFY` signals — never call `QML` methods directly from Python.
- Long-running work (simulation, file I/O, HTTP) goes in a `QRunnable` submitted to `QThreadPool.globalInstance()`. The worker emits a signal on completion.
- Register ViewModels with `engine.rootContext().setContextProperty(...)` in `main.py`. Do not create global singletons.
- Store user preferences (theme, last open plan, window geometry) in `QSettings`. Use `QStandardPaths.AppDataLocation` for the database file path. Import org/app/DB constants from `src/app/identity.py` — do not scatter string literals.

### QML

- Use `Material` style (Qt Quick Controls 2). Respect `Material.theme` for dark/light mode.
- All user-visible strings must be wrapped in `qsTr()` for future i18n.
- Prefer property bindings over imperative `onSignalChanged` handlers where possible.
- Component file names are `PascalCase.qml`. Internal IDs are `camelCase`.
- Never put business logic in QML. QML calls `@Slot` methods on ViewModels; ViewModels own all logic.

### SQLAlchemy / Data Layer

- Use **SQLAlchemy Core** (not ORM). All queries use bound parameters — never string-concatenate SQL.
- Repositories are the **only** classes that access the database session. Business logic never touches the session directly.
- Every new table or column requires an **Alembic migration**. Run `alembic upgrade head` to verify before opening a PR.
- Abstract repository interfaces live in `src/data/repositories/`. Inject concrete implementations at startup to enable in-memory test doubles.

### Pydantic v2

- Domain entities (`Plan`, `Entry`, `FinancialEvent`, etc.) are Pydantic `BaseModel`s.
- Immutable value objects use `model_config = ConfigDict(frozen=True)`.
- Validate all external input (user form data, CSV imports, API responses) through a Pydantic model before any DB write.

### Testing

- **Unit tests** (`tests/unit/`) — pure Python, no Qt, no file system. Use `pytest` + `hypothesis` for property-based tests.
- **Integration tests** (`tests/integration/`) — `pytest-qt` + in-memory SQLite (`:memory:`). Test ViewModel ↔ Repository interactions.
- **E2E tests** (`tests/e2e/`) — `pytest-qt` with `QT_QPA_PLATFORM=offscreen` against a temp database.
- Coverage targets: `date_pattern.py` and event expander at 100%; simulation engine and currency normalizer at 95%.
- New features must include unit tests. New ViewModels must include integration tests.

---

## Project Conventions

### File & Module Layout

Follow the structure defined in `docs/DESIGN.md` §4.2:

```
src/app/viewmodels/   — QObject subclasses (ViewModel per page/feature)
src/app/identity.py   — canonical platform identifiers (org/app names, DB filename, PyPI name)
src/app/identity_migration.py — one-time upgrade path from legacy Financial Tracker paths
src/app/models/       — QAbstractListModel subclasses
src/domain/           — Pure Python: entities, simulation, date pattern, currency
src/data/             — Repositories, schema, migrations
src/export/           — CSV / PDF exporters
src/integrations/     — Optional: import service, exchange rate fetcher
qml/pages/            — Full-page QML views
qml/components/       — Reusable QML components
tests/unit/
tests/integration/
```

### Naming

| Artifact | Convention | Example |
|----------|-----------|---------|
| Python files | `snake_case.py` | `simulation_engine.py` |
| QML files | `PascalCase.qml` | `BalanceChart.qml` |
| ViewModel classes | `<Feature>ViewModel` | `SimulationViewModel` |
| Repository classes | `Sqlite<Entity>Repository` | `SqliteEntryRepository` |
| Qt signals | `camelCaseChanged` | `isRunningChanged` |
| `Q_PROPERTY` names | `camelCase` | `isRunning`, `result` |

### Error Handling

- Business logic raises **typed exceptions** (e.g., `DatePatternParseError`, `CurrencyConversionError`). These are plain Python — no Qt imports.
- ViewModels catch all exceptions in `@Slot` methods, set the `error` Q_PROPERTY, and emit the `errorChanged` signal. They never re-raise into QML.
- QML binds an `InfoBar` to `viewModel.error !== ""`. Dismiss calls `viewModel.clearError()`.

---

## GitHub Issues & Project Workflow

Work is tracked on **GitHub Issues** and the
[project board](https://github.com/users/sekurado/projects/2). Completed Stories 1–30 are archived in
[`docs/DEVELOPMENT_HISTORY.md`](docs/DEVELOPMENT_HISTORY.md).

### Issue Types

| Type | When to create | Project field **Type** |
|------|----------------|------------------------|
| Story | New feature epic spanning multiple tasks | `Story` |
| Task | Single implementable unit of work | `Task` |
| Bug | Defect or regression | `Task` (or add a Bug label if used) |

### Workflow Rules

1. **Plan mode** — create a GitHub Issue with the full spec in the body before writing any code.
2. **Project** — add the issue to [Project #2](https://github.com/users/sekurado/projects/2).
3. **Fields** — set **Type** (Story or Task), **Story** (parent story issue link for tasks), and **Status** (Todo → In Progress → Done). **Status lives only on the project board** — do not duplicate it in issue bodies.
4. **Start story** — when implementation on a story begins, move the **Story** issue **Status** → **In Progress** on the project board.
5. **Start task** — **first action before any implementation** (see **Starting a task (agents)** below). Move that **Task** issue **Status** → **In Progress** on the project board; only one task should be in progress at a time.
6. **Commit** — when task implementation is complete, **stop for user review** before committing. After approval, commit with subject line `<task_number>: <short description>` (e.g. `31_2: Schema, migration, repositories and label search`), move project **Status** to **Done**, and add `Closes #N` (or `Fixes #N`) in the commit body on its own line with **no trailing punctuation** (use `Closes #7`, not `Closes #7.`). GitHub closes the linked issue when that commit is **pushed** — on any branch, not only after merge to `main`. **Do not commit without explicit user approval.**
7. **Task complete checklist** — after the approved commit (and push, if requested): update project **Status** → **Done**; confirm the issue closed (fix keyword or close manually if not).
8. **Pull request** — open a PR to merge the branch into `main`. Do not repeat `Closes #N` if the task issue is already closed; reference the issue for traceability instead.
9. **Story complete** — close the story issue when all child task issues are closed; update `docs/DESIGN.md` if architecture changed.

**Issue state vs project Status:** project **Status** → Done tracks implementation complete; issue **closed** tracks a pushed commit or merged PR with `Closes #N` / `Fixes #N`. Do not use closing keywords until the task is actually done.

### Starting a task (agents)

When the user says **start next task**, names a task issue, or you begin work on a task:

1. **Move the project card first** — set that task's **Status** → **In Progress** on [Project #2](https://github.com/users/sekurado/projects/2) via GraphQL or `gh` (below). Do this **before** reading code for implementation, editing files, or running task-specific tests.
2. **First task on a story** — also move the parent **Story** issue **Status** → **In Progress** if it is still **Todo**.
3. **Do not skip or defer** — never assume a prior session moved the card; if it is still **Todo**, update it now. Tell the user the card was moved (include issue number).
4. **One task in flight** — only one task should be **In Progress** at a time.

Repo issue state (open/closed) is separate from project **Status** — closing keywords in commits do not move the board.

### Updating project Status (agents)

GitHub MCP `issue_write` + `issue_fields` updates **repo** issue fields only — not project board **Status**, **Type**, or **Story** on [Project #2](https://github.com/users/sekurado/projects/2).

Use the **GitHub GraphQL API** with `GITHUB_SEKURADO_PAT` (or `GITHUB_TOKEN`) and `updateProjectV2ItemFieldValue` on `user(login: "sekurado").projectV2(number: 2)`. If `gh` is installed and authenticated (`project` scope), `gh project item-edit` works too. Try one of these before asking the user to drag cards manually.

Never log, echo, commit, or paste `GITHUB_SEKURADO_PAT`, `GITHUB_TOKEN`, or any `ghp_` / `github_pat_` value — read tokens only from the environment inside scripts.

### Story → Issue Map (31–35)

| Story | Issue |
|-------|-------|
| 31 Actual Expense Tracking | [#2](https://github.com/sekurado/cash-flow-planner-app/issues/2) |
| 32 Expense Analytics | [#3](https://github.com/sekurado/cash-flow-planner-app/issues/3) |
| 33 Receipt-Assisted Entry | [#4](https://github.com/sekurado/cash-flow-planner-app/issues/4) |
| 34 Journal Backup & Cloud | [#5](https://github.com/sekurado/cash-flow-planner-app/issues/5) |
| 35 Open Source Readiness | [#6](https://github.com/sekurado/cash-flow-planner-app/issues/6) |

Do **not** create files under `tasks/` — that legacy folder was removed. Put specs directly in issue bodies.

**Starting a task:** move project **Status** → **In Progress** as the **first** step (GraphQL/`gh`), before any implementation — see **Starting a task (agents)** above.
When starting a story (first task on that story), move the **Story** issue **Status** → **In Progress** on the project board too.
When committing completed task work, **wait for explicit user approval** after implementation is ready for review. Then use subject line `<task_number>: <short description>`, add `Closes #N` in the commit body (no trailing period), move the task's project **Status** to **Done** in the **same session** via GraphQL/`gh`, and confirm the issue closed after push. **Never commit without user review.** Never leave project **Status** at In Progress or Todo after the implementation commit.

Never add `Co-authored-by` (or any other commit-message trailer) unless the user explicitly requests it. Cursor `beforeShellExecution` hooks deny `git commit` when the command contains that trailer (rule: `scripts/harness/rules/no_coauthored_by.py`). Do not bypass hooks with `--no-verify`.

---

## Documentation Rules

- **Always update `docs/DESIGN.md`** when an architectural decision changes, a new module is added, or a design decision from the appendix is revisited.
- **Always update `docs/README.md`** when a new document is added to `docs/`.
- Supplementary docs (how-to guides for specific subsystems) live in `docs/` alongside `DESIGN.md`.
- Docs are written in Markdown. Diagrams use Mermaid fenced code blocks (`\`\`\`mermaid`).

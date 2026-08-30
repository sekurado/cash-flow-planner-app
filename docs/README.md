# Documentation Index

This folder contains all design and architectural documentation for **Cash Flow Planner Desktop**.

> Keep this index up to date whenever a document is added, removed, or renamed.

---

## Documents

| Document | Description |
|----------|-------------|
| [DESIGN.md](./DESIGN.md) | System design document — full architecture, domain model, tech stack decisions, data flow diagrams, and non-functional requirements. The primary reference for the system. |
| [BUILD.md](./BUILD.md) | Local build guide — prerequisites, one-command installer builds for macOS, Windows, and Linux, and notes for sharing unsigned builds. |
| [pitch/README.md](./pitch/README.md) | Positioning one-pager — problem, solution, audience, and differentiators for stakeholders and future marketing use. |
| [TERMINOLOGY.md](./TERMINOLOGY.md) | UI vs internal naming glossary — professional user-facing terms (`Forecast`, `Cash flow`, `Cash shortfall`) mapped to unchanged code identifiers (`Plan`, `Entry`, `plan_id`). |
| [DEVELOPMENT_HISTORY.md](./DEVELOPMENT_HISTORY.md) | Story-level roadmap archive (Stories 1–30 completed under legacy `tasks/` workflow; Stories 31+ on GitHub Issues). |
| [manual/CashFlowPlanner-UserManual_en.pdf](./manual/CashFlowPlanner-UserManual_en.pdf) | Bundled **user manual** PDFs (reference copies for en, fr, ru, es, de). Regenerate with `python scripts/generate_manual.py --all`. See [manual/README.md](./manual/README.md). |

---

## How Docs Are Maintained

- **DESIGN.md** is the authoritative system design (current version: 1.6). Update it whenever a significant architectural decision is made, a new layer or module is introduced, or an existing design decision is reversed.
- Supplementary docs (to be added here as the project grows) describe **how specific subsystems work** in more operational detail — e.g., the simulation pipeline, the date pattern parser, QML component conventions, or database migration runbook.
- After every feature or story is completed, review whether any doc is stale and update it as part of the task's definition of done.

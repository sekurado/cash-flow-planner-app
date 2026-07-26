# Development History

This document archives the story-level roadmap for **Cash Flow Planner Desktop**.
Detailed specs for completed work (Stories 1–30) lived in the legacy `tasks/` folder and remain
recoverable from git history. **Active work** (Stories 31–35) is tracked on
[GitHub Issues](https://github.com/sekurado/cash-flow-planner-app/issues) and the
[project board](https://github.com/users/sekurado/projects/2).

---

## Progress overview

| Story | Title | Status | Tasks | Tracking |
|-------|-------|--------|-------|------------|
| 1 | Project Foundation & Infrastructure | done | 6 | Legacy `tasks/` (git history) |
| 2 | Domain Model & Date Pattern System | done | 6 | Legacy `tasks/` (git history) |
| 3 | Data Layer: Schema, Migrations & Repositories | done | 6 | Legacy `tasks/` (git history) |
| 4 | Simulation Engine | done | 4 | Legacy `tasks/` (git history) |
| 5 | Application Layer: ViewModels & Qt List Models | done | 8 | Legacy `tasks/` (git history) |
| 6 | Presentation Layer: QML Pages & Components | done | 11 | Legacy `tasks/` (git history) |
| 7 | CSV & Excel Import | done | 4 | Legacy `tasks/` (git history) |
| 8 | Export: CSV & PDF | done | 4 | Legacy `tasks/` (git history) |
| 9 | Multi-Currency Support & Optional Live Rate Fetching | done | 4 | Legacy `tasks/` (git history) |
| 10 | What-If Simulation Mode | done | 2 | Legacy `tasks/` (git history) |
| 11 | Calendar-View Date Picker | done | 1 | Legacy `tasks/` (git history) |
| 12 | Build & Release Pipeline | done | 6 | Legacy `tasks/` (git history) |
| 13 | App-wide Settings & Multi-language Support | done | 4 | Legacy `tasks/` (git history) |
| 14 | UI Rework: Modern Theme & Visual Language | done | 6 | Legacy `tasks/` (git history) |
| 15 | USD-Only Plan Base & Simulation Display Currency | done | 5 | Legacy `tasks/` (git history) |
| 16 | Plan Export & Import | done | 5 | Legacy `tasks/` (git history) |
| 17 | Plan Base Currency & Exchange Rate Bulk Actions | done | 5 | Legacy `tasks/` (git history) |
| 18 | Open Access Exchange Rates (No API Key) | done | 1 | Legacy `tasks/` (git history) |
| 19 | Product Positioning & Brand Messaging | done | 4 | Legacy `tasks/` (git history) |
| 20 | Professional Terminology (UI Copy) | done | 5 | Legacy `tasks/` (git history) |
| 21 | Executive PDF Reports | done | 5 | Legacy `tasks/` (git history) |
| 22 | Forecast Templates (Onboarding) | done | 5 | Legacy `tasks/` (git history) |
| 23 | Trust & Transparency | done | 6 | Legacy `tasks/` (git history) |
| 24 | Platform Identity Rename (Tracker → Planner) | done | 1 | Legacy `tasks/` (git history) |
| 25 | Executive PDF Refinement | done | 2 | Legacy `tasks/` (git history) |
| 26 | Balance Chart Hover Tooltip | done | 2 | Legacy `tasks/` (git history) |
| 27 | Visual PDF Export (Color Coding & Balance Chart) | done | 6 | Legacy `tasks/` (git history) |
| 28 | Windows Install Integrity & UI Fixes | done | 6 | Legacy `tasks/` (git history) |
| 29 | User Manual PDF (Modern Rich Document) | done | 7 | Legacy `tasks/` (git history) |
| 30 | Cash-Flow Suggestions Engine | done | 6 | Legacy `tasks/` (git history) |
| 31 | Actual Expense Tracking (Phase 1) | in progress | 6 | [Issue #2](https://github.com/sekurado/cash-flow-planner-app/issues/2) |
| 32 | Expense Analytics & Search (Phase 2) | todo | 5 | [Issue #3](https://github.com/sekurado/cash-flow-planner-app/issues/3) |
| 33 | Receipt-Assisted Expense Entry (Phase 3) | todo | 5 | [Issue #4](https://github.com/sekurado/cash-flow-planner-app/issues/4) |
| 34 | Spending Journal Backup & Cloud Sync | todo | 6 | [Issue #5](https://github.com/sekurado/cash-flow-planner-app/issues/5) |
| 35 | Open Source & Repository Publish Readiness | todo | 6 | [Issue #6](https://github.com/sekurado/cash-flow-planner-app/issues/6) |

**Total tasks (original roadmap):** 171

---

## Legacy workflow (Stories 1–30)

Stories 1–30 were planned and completed using markdown files under `tasks/` (`todo/`,
`inprogress/`, `done/`) with `tasks/INDEX.md` as the index. That folder was
removed when tracking moved to GitHub Issues. To inspect old task specs, check out an earlier
commit that still contains `tasks/`.

---

## Current workflow (Stories 31+)

- **Stories** — GitHub Issues [#2](https://github.com/sekurado/cash-flow-planner-app/issues/2)–[#6](https://github.com/sekurado/cash-flow-planner-app/issues/6) (epic-level)
- **Tasks** — Child issues linked on the [project board](https://github.com/users/sekurado/projects/2) with **Type** = Task and **Story** field set
- **Status** — Project **Status** column (Todo / In Progress / Done) and issue open/closed state
- **PRs** — Use `Fixes #N` in the PR description to close the task issue on merge

See [AGENTS.md](../AGENTS.md) and [`.cursor/rules/task-workflow.mdc`](../.cursor/rules/task-workflow.mdc)
for agent and contributor workflow.

---

## Dependency order (Stories 31–35)

```
Story 31 (Actual Expense Tracking) ── depends on Stories 3, 5, 6, 9, 13, 20
Story 32 (Expense Analytics) ── depends on Story 31, 6, 9, 14
Story 33 (Receipt-Assisted Entry) ── depends on Story 31, 6
Story 34 (Journal Backup & Cloud) ── depends on Story 31, 5, 6, 13, 16; optional Story 33
Story 35 (Open Source & Publish) ── depends on Stories 12, 19, 24; independent of 31–34
```

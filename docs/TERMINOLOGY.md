# Terminology Glossary

Authoritative reference for **user-facing (UI) copy** vs **internal code identifiers** in Cash Flow Planner Desktop.

---

## Purpose

The app targets professional users — fractional CFOs, consultants, and small-business operators — who expect cash-flow forecasting vocabulary, not personal-finance jargon.

- **UI copy** (QML `qsTr()` strings, translation files, export headers, and `user_messages.py` templates shown to users) uses the **professional terms** in the glossary below.
- **Code, database, and file formats** keep **legacy internal names** (`Plan`, `Entry`, `plan_id`, `.ftplan`, repository classes, DB tables) for backward compatibility and to avoid a disruptive rename across the stack.

When adding or changing user-visible text, consult this document first. When writing Python domain logic, repositories, or migrations, keep internal names unchanged.

---

## Glossary

| Current (UI) | New (UI) | Internal (unchanged) | Notes |
|--------------|----------|----------------------|-------|
| Plan | Forecast | `Plan`, `plans` table | Singular noun in lists, detail headers, and dialogs |
| Plans | Forecasts | `PlanViewModel`, `PlanListPage.qml` | Plural navigation and page titles |
| New Plan | New forecast | — | Action buttons and empty-state CTAs |
| Entries | Cash flows | `Entry`, `entries` table | Section headings and list summaries |
| Entry | Cash flow / Line item | `Entry`, `EntryForm.qml` | See [Context rules](#context-rules) |
| Deficit | Cash shortfall | `first_deficit_date`, `DeficitBanner.qml` | Banner text, table columns, export headers |
| Simulation | Forecast run / Projection | `SimulationEngine`, `SimulationPage.qml` | Page titles and run controls; prefer **Forecast run** for actions, **Projection** for results |
| What-if | Scenario | what-if overrides, `WhatIfPanel.qml` | Panel title and override labels |
| Suggestion | Suggestion | `SuggestionsPanel.qml`, `SuggestionEngine` | Use **Suggestion** (not "Recommendation") for forecast analysis hints |
| Import plan | Import forecast | `.ftplan` extension | File-picker and menu labels; extension stays `.ftplan` |
| — | Spending | `RecordedExpensesPage.qml` | Top-level nav tab for the spending journal (not "Budget") |
| — | Recorded expense | `recorded_expenses` table, `RecordedExpenseService` | Singular transaction in the spending journal; avoid "budget" or "envelope" |

### Product name exception

The product name **Cash Flow Planner** (chosen in Story 19) may appear in window titles, about text, and marketing copy. Do not retroactively replace "plan" inside the product name.

---

## Context rules

### Cash flow vs Line item

| Context | Use | Example |
|---------|-----|---------|
| Section or list heading (collection) | **Cash flows** | "Cash flows for this forecast" |
| Singular row, form, or dialog title | **Cash flow** | "Edit cash flow", "Add cash flow" |
| Table cell or inline reference to one row in a grid | **Line item** | Monthly table row label when distinguishing from the aggregate section |
| Error messages referencing a missing record | **Cash flow** | "Cash flow not found: …" |

When both fit, prefer **cash flow** for user actions (add, edit, delete) and **line item** only where the UI shows a single row inside a larger cash-flow table or projection grid.

### Cash shortfall vs Deficit

Always use **cash shortfall** (or **shortfall** when space is tight) in UI copy and export headers. The internal field `deficit` on `MonthlySnapshot` and `first_deficit_date` on simulation results stay as-is in Python and SQL.

### Forecast run vs Projection

| Context | Use | Example |
|---------|-----|---------|
| Button or menu action to execute | **Run forecast** / **Forecast run** | "Run forecast" button |
| Page or tab showing results | **Projection** | "Projection" tab, chart subtitle |
| Export document title | **Projection report** | PDF title: `{name} — Projection report` |
| Background/worker status | **Running forecast…** | Progress or loading state |

### Scenario (formerly What-if)

Use **scenario** for panel titles, override toggles, and help text. Internal code may still refer to "what-if overrides" in variable names and comments.

---

## Files affected

Subsequent Story 20 tasks update user-visible strings in these locations. Internal identifiers in the same files are **not** renamed.

### QML (`qml/`)

| File | Typical strings |
|------|-----------------|
| `main.qml` | Navigation labels, app chrome |
| `pages/RecordedExpensesPage.qml` | Spending journal list, empty state |
| `pages/PlanListPage.qml` | Forecast list, "New forecast" |
| `pages/PlanDetailLayout.qml` | Tab labels, forecast context |
| `pages/EntriesPage.qml` | Cash flows section |
| `pages/SimulationPage.qml` | Projection / forecast run |
| `pages/SettingsPage.qml` | Settings copy |
| `components/DeficitBanner.qml` | Cash shortfall warning |
| `components/SuggestionsPanel.qml` | Cash-flow suggestions after a projection |
| `components/WhatIfPanel.qml` | Scenario overrides |
| `components/SimulationControls.qml` | Run forecast controls |
| `components/EntryForm.qml`, `EntryFormDrawer.qml` | Add/edit cash flow |
| `components/RecordedExpenseFormDrawer.qml`, `LabelAutocompleteField.qml` | Add/edit recorded expense |
| `components/PlanImportDialog.qml`, `ImportDialog.qml` | Import forecast |
| `components/MonthlyTableView.qml`, `BalanceChart.qml` | Projection display |
| `components/DatePatternInput.qml`, `DatePicker.qml`, `CurrencyRateEditor.qml` | Form helpers |

QML **file names** stay unchanged (e.g. `PlanListPage.qml`, `DeficitBanner.qml`).

### i18n

| File | Role |
|------|------|
| `i18n/app_en.ts` | English source strings |
| `i18n/app_fr.ts` | French translations |
| `i18n/app_ru.ts` | Russian translations |
| `i18n/app_es.ts` | Spanish translations |
| `i18n/app_de.ts` | German translations |

Run `pyside6-lupdate` after QML changes to refresh `.ts` files, then update all five locales.

### Python — UI error templates

| File | Role |
|------|------|
| `src/app/i18n/user_messages.py` | Maps domain exceptions to translatable UI strings (e.g. `Plan not found` → `Forecast not found`) |
| `src/app/i18n/suggestion_copy.py` | Localizes `CashFlowSuggestions` templates for suggestion cards |

Domain-layer exception messages in `src/domain/` may remain internal; only strings routed through ViewModels for display need the glossary terms.

### Export

| File | Typical strings |
|------|-----------------|
| `src/export/pdf_exporter.py` | Report title, column headers |
| `src/export/csv_exporter.py` | CSV column headers |

### Tests

| Location | Role |
|----------|------|
| `tests/e2e/` | Assertions on visible UI strings |
| `tests/unit/test_user_messages.py` | Error template expectations |

---

## Do not rename

The following identifiers are **frozen** for compatibility. UI copy must not force renames here.

| Category | Examples |
|----------|----------|
| Domain entities | `Plan`, `Entry`, `FinancialEvent`, `SimulationResult` |
| Database | `plans`, `entries` tables; columns `plan_id`, `first_deficit_date` |
| Repositories | `SqlitePlanRepository`, `SqliteEntryRepository`, `AbstractPlanRepository` |
| ViewModels | `PlanViewModel`, `EntriesViewModel`, `SimulationViewModel` |
| QML file names | `PlanListPage.qml`, `EntriesPage.qml`, `DeficitBanner.qml`, `WhatIfPanel.qml` |
| File format | `.ftplan` extension, `PlanExportBundle`, `PlanExporter` |
| Simulation engine | `SimulationEngine`, `run_simulation()` |

New code should continue using these internal names. Apply glossary terms only in strings shown to users (`qsTr()`, `.ts` files, export headers, and `user_messages.py` display templates).

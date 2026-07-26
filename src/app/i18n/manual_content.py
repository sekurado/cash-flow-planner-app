from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from PySide6.QtCore import QCoreApplication

_CONTEXT = "UserManual"

MANUAL_VERSION = "1.0"


class ManualBlockType(StrEnum):
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet_list"
    TIP = "tip"
    NOTE = "note"
    IMPORTANT = "important"
    PATTERN_TABLE = "pattern_table"


@dataclass(frozen=True)
class ManualBlock:
    block_type: ManualBlockType
    text: str
    title: str | None = None


@dataclass(frozen=True)
class ManualSection:
    heading: str
    blocks: tuple[ManualBlock, ...]


@dataclass(frozen=True)
class ManualChapter:
    title: str
    sections: tuple[ManualSection, ...]


def _translate(source: str) -> str:
    return QCoreApplication.translate(_CONTEXT, source)


def _paragraph(text: str) -> ManualBlock:
    return ManualBlock(block_type=ManualBlockType.PARAGRAPH, text=_translate(text))


def _bullets(*items: str) -> ManualBlock:
    return ManualBlock(
        block_type=ManualBlockType.BULLET_LIST,
        text="\n".join(_translate(item) for item in items),
    )


def _tip(body: str, title: str | None = None) -> ManualBlock:
    return ManualBlock(
        block_type=ManualBlockType.TIP,
        text=_translate(body),
        title=_translate(title) if title is not None else None,
    )


def _note(body: str, title: str | None = None) -> ManualBlock:
    return ManualBlock(
        block_type=ManualBlockType.NOTE,
        text=_translate(body),
        title=_translate(title) if title is not None else None,
    )


def _important(body: str, title: str | None = None) -> ManualBlock:
    return ManualBlock(
        block_type=ManualBlockType.IMPORTANT,
        text=_translate(body),
        title=_translate(title) if title is not None else None,
    )


def _pattern_table(caption: str, rows: tuple[tuple[str, str], ...]) -> ManualBlock:
    lines = [f"{pattern}\t{description}" for pattern, description in rows]
    return ManualBlock(
        block_type=ManualBlockType.PATTERN_TABLE,
        text="\n".join(lines),
        title=_translate(caption),
    )


def manual_title() -> str:
    return _translate("Cash Flow Planner")


def manual_subtitle() -> str:
    return _translate("User Manual")


def manual_chapters() -> tuple[ManualChapter, ...]:
    return (
        ManualChapter(
            title=_translate("Welcome"),
            sections=(
                ManualSection(
                    heading=_translate("About Cash Flow Planner"),
                    blocks=(
                        _paragraph(
                            "Cash Flow Planner is an offline-first cash-flow forecasting "
                            "application for individuals and small businesses. You define "
                            "income and expense cash flows, run projections over a chosen "
                            "horizon, and review a running balance that shows when a cash "
                            "shortfall may occur."
                        ),
                        _paragraph(
                            "All forecasts, cash flows, and exchange rates are stored "
                            "locally in a SQLite database on your computer. The app does "
                            "not require an account, sign-in, or continuous internet "
                            "connection to build and run forecasts."
                        ),
                        _tip(
                            "Your data never leaves your device unless you explicitly "
                            "export a file or share a backup."
                        ),
                        _important(
                            "Cash Flow Planner does not provide automatic cloud backup. "
                            "Use Export forecast to save a .ftplan file if you need a "
                            "portable copy of your work."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Who this manual is for"),
                    blocks=(
                        _paragraph(
                            "This manual is written for freelancers, business operators, "
                            "fractional CFOs, and advisors who need a practical cash-flow "
                            "forecast without enterprise complexity. Whether you manage "
                            "personal income swings or a small company's payroll and "
                            "vendor payments, the same workflow applies."
                        ),
                        _bullets(
                            "Build a forecast from scratch or start from a bundled template",
                            "Model recurring and one-time cash flows with compact date patterns",
                            "Run projections and spot the first cash shortfall before it happens",
                            "Explore scenarios without overwriting saved cash flows",
                        ),
                        _tip(
                            "Throughout the app, user-facing text uses professional "
                            "forecasting vocabulary—Forecast, Cash flow, Cash shortfall, "
                            "and Scenario—rather than personal-finance jargon."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("Getting started"),
            sections=(
                ManualSection(
                    heading=_translate("First launch"),
                    blocks=(
                        _paragraph(
                            "When you launch Cash Flow Planner for the first time, the "
                            "Forecasts page is empty. The app creates a local database "
                            "automatically in your platform application-data folder, so "
                            "you can start working immediately."
                        ),
                        _paragraph(
                            "The main navigation shell keeps Forecasts as your home view. "
                            "Open Settings from the gear icon in the app header to adjust "
                            "appearance and language before you create your first forecast."
                        ),
                        _tip(
                            "Switch Dark mode and Language in Settings without restarting "
                            "the application—the interface updates live."
                        ),
                        _note(
                            "If you reinstall the app on the same machine, your existing "
                            "database is preserved in the application-data location."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Create a forecast"),
                    blocks=(
                        _paragraph(
                            "Select New forecast on the Forecasts page. A dialog asks "
                            "whether to start with a blank forecast or use a template. "
                            "For a blank forecast, enter a descriptive name, choose the "
                            "forecast base currency, and set the opening cash balance."
                        ),
                        _paragraph(
                            "After creation, the forecast detail view opens with three "
                            "tabs: Cash flows, Projection, and Change history. Add cash "
                            "flows on the first tab, then move to Projection when you "
                            "are ready to run a forecast."
                        ),
                        _tip(
                            "Pick the base currency carefully—it is the currency used to "
                            "sum cash flows during a projection run. Other currencies "
                            "convert using exchange rates from Settings."
                        ),
                        _important(
                            "Each forecast is independent. Deleting a forecast removes "
                            "its cash flows and projection history for that forecast only."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Start from a template"),
                    blocks=(
                        _paragraph(
                            "When you choose From template in the New forecast dialog, "
                            "the template picker lists bundled starting points such as "
                            "freelancer, small business, and household cash-flow examples. "
                            "Each card shows a short description of what the template "
                            "includes."
                        ),
                        _paragraph(
                            "After you select a template and confirm a forecast name, "
                            "Cash Flow Planner creates the forecast and pre-fills typical "
                            "income and expense cash flows. Every line item remains fully "
                            "editable—templates are a shortcut, not a constraint."
                        ),
                        _tip(
                            "Templates are ideal for onboarding: review each pre-filled "
                            "cash flow, adjust amounts to match your situation, and delete "
                            "lines you do not need."
                        ),
                        _important(
                            "Choosing a template does not lock currency or patterns. "
                            "You can change any field immediately after creation."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("Cash flows"),
            sections=(
                ManualSection(
                    heading=_translate("Add income and expenses"),
                    blocks=(
                        _paragraph(
                            "Open a forecast and select the Cash flows tab. Income and "
                            "expense cash flows are listed separately so you can scan "
                            "inflows and outflows at a glance. Use the Add cash flow "
                            "floating action button to open the cash flow drawer."
                        ),
                        _paragraph(
                            "In the drawer, choose whether the line is income or expense, "
                            "enter a name and amount, pick a currency, and type a date "
                            "pattern. The pattern preview label below the field updates "
                            "as you type so you can confirm the schedule before saving."
                        ),
                        _bullets(
                            "Income cash flows increase your balance on scheduled dates",
                            "Expense cash flows decrease your balance on scheduled dates",
                            "Use Import on the Cash flows page to load rows from CSV or Excel",
                        ),
                        _tip(
                            "Give each cash flow a clear name—projection results and the "
                            "cash shortfall banner reference these names when highlighting "
                            "contributing line items."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Date patterns"),
                    blocks=(
                        _paragraph(
                            "Every cash flow is scheduled with a compact date pattern "
                            "instead of picking individual calendar dates. Patterns can "
                            "represent daily, monthly, yearly, or one-time events. The "
                            "syntax is validated while you edit, and invalid patterns "
                            "show an error before you save."
                        ),
                        _paragraph(
                            "Examples include ... for every day, 10.. for monthly on the "
                            "10th, 15.03. for yearly on 15 March, and 15.03.2026 for a "
                            "single occurrence. The live description under the pattern "
                            "field restates the schedule in plain language."
                        ),
                        _tip(
                            "If a pattern looks wrong, check the preview label before "
                            "saving—a small typo can shift every occurrence in the "
                            "projection range."
                        ),
                        _note(
                            "The Quick reference chapter at the end of this manual lists "
                            "common patterns in a cheat sheet table."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Edit and delete"),
                    blocks=(
                        _paragraph(
                            "Tap or click a cash flow in the list to reopen the drawer "
                            "in Edit cash flow mode. Changes save to the forecast "
                            "immediately when you confirm. Amount, currency, pattern, and "
                            "active state can all be updated."
                        ),
                        _paragraph(
                            "Use delete inside the drawer to remove a cash flow you no "
                            "longer need. After any edit, return to the Projection tab "
                            "and run the forecast again so monthly summaries and the "
                            "balance chart reflect your latest data."
                        ),
                        _tip(
                            "Deactivate a line item temporarily using the Scenario panel "
                            "on the Projection tab if you only want to test removing it."
                        ),
                        _important(
                            "Edits on the Cash flows tab are saved permanently to your "
                            "forecast. Scenario overrides on the Projection tab are not."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("Running a projection"),
            sections=(
                ManualSection(
                    heading=_translate("Set horizon and opening balance"),
                    blocks=(
                        _paragraph(
                            "Select the Projection tab to configure and run a forecast. "
                            "Choose the projection start date, end date (horizon), and "
                            "confirm the opening cash balance. The controls at the top "
                            "of the page apply to the current forecast run."
                        ),
                        _paragraph(
                            "Press Run forecast to expand every active cash flow across "
                            "the date range, convert foreign currencies to the forecast "
                            "base currency, and compute a day-by-day running balance. "
                            "While the run is in progress, the button shows a busy state."
                        ),
                        _tip(
                            "Re-run the forecast after you change cash flows, exchange "
                            "rates, or the horizon so tables and charts stay current."
                        ),
                        _note(
                            "If a required exchange rate is missing, the run stops with a "
                            "clear error—add the rate in Settings and try again."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Read the monthly table"),
                    blocks=(
                        _paragraph(
                            "Below the controls, the monthly table aggregates each month "
                            "in the projection range. Columns typically include opening "
                            "balance, inflows, outflows, net flow, and closing balance. "
                            "Amounts use semantic coloring—inflows in green and outflows "
                            "in red—so trends are easy to scan."
                        ),
                        _paragraph(
                            "Months where the closing balance falls below zero are treated "
                            "as a cash shortfall. Those rows receive an amber highlight so "
                            "you can spot problem periods without reading every number."
                        ),
                        _tip(
                            "Compare consecutive months to see whether a shortfall is a "
                            "one-month timing gap or a sustained cash-flow problem."
                        ),
                        _important(
                            "The table shows monthly snapshots. The cash shortfall banner "
                            "reports the first day the daily balance drops below zero, "
                            "which may fall mid-month."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Balance chart"),
                    blocks=(
                        _paragraph(
                            "The balance chart plots your running balance across the "
                            "projection horizon. The area above zero uses the primary "
                            "brand color; when the balance drops below zero, the chart "
                            "fills the deficit region in red so shortfalls stand out "
                            "visually."
                        ),
                        _paragraph(
                            "Move the pointer over the chart to show a vertical guide "
                            "line, the nearest data point, and a tooltip with the date "
                            "and balance for that day. This is useful for pinpointing "
                            "when a decline begins."
                        ),
                        _tip(
                            "Use the chart together with the monthly table—the chart "
                            "shows timing within a month; the table summarizes totals."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Cash shortfall alert"),
                    blocks=(
                        _paragraph(
                            "When a projection finds a day with a negative closing balance, "
                            "a dismissible cash shortfall banner appears at the top of "
                            "the Projection tab. It names the first shortfall date and "
                            "the expense cash flow that contributed on that day."
                        ),
                        _paragraph(
                            "Address a shortfall by adjusting timing or amounts on the "
                            "Cash flows tab, adding income, or opening the Scenario panel "
                            "to test changes before you commit them. Dismiss the banner "
                            "when you have noted the date—it reappears on the next run "
                            "if the shortfall still exists."
                        ),
                        _important(
                            "Only the earliest cash shortfall in a run is reported. Later "
                            "shortfalls during the same projection are not listed "
                            "separately."
                        ),
                        _tip(
                            "Export an executive report after a run to share projection "
                            "results, including the balance chart, with stakeholders."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("What-if scenarios"),
            sections=(
                ManualSection(
                    heading=_translate("Enable overrides"),
                    blocks=(
                        _paragraph(
                            "The Scenario panel on the Projection tab lets you explore "
                            "what-if changes without altering saved cash flows. Expand "
                            "the panel to see each active line item with override "
                            "controls for amount and whether the line is active in the "
                            "current run."
                        ),
                        _paragraph(
                            "Adjust an amount or deactivate a line, then run the forecast "
                            "again. The projection engine applies overrides only for "
                            "that run, leaving your stored forecast unchanged on the "
                            "Cash flows tab."
                        ),
                        _tip(
                            "Use scenarios to test hiring, deferring a payment, or "
                            "pausing a subscription before you edit the baseline forecast."
                        ),
                        _important(
                            "Scenario overrides are never saved to your forecast. Clear "
                            "overrides or close the panel to return to the saved baseline."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Compare with baseline"),
                    blocks=(
                        _paragraph(
                            "After you enable overrides, run the forecast to see updated "
                            "monthly balances, chart shape, and cash shortfall timing. "
                            "Compare the results mentally with your last baseline run, or "
                            "note which line items you changed in the Scenario panel."
                        ),
                        _paragraph(
                            "When you export an executive report while overrides are "
                            "active, the PDF can include a scenario comparison section "
                            "that contrasts key metrics between the baseline and the "
                            "current scenario run."
                        ),
                        _tip(
                            "Toggle overrides off line by line to isolate which change "
                            "moved the first cash shortfall date."
                        ),
                        _note(
                            "Change history on the forecast detail tab records edits to "
                            "saved cash flows, not temporary scenario overrides."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("Import & export"),
            sections=(
                ManualSection(
                    heading=_translate("Import CSV/Excel"),
                    blocks=(
                        _paragraph(
                            "On the Cash flows tab, select Import to open the import "
                            "dialog. Choose a CSV or Excel file from your computer and "
                            "map file columns to name, amount, type (income or expense), "
                            "currency, and date pattern."
                        ),
                        _paragraph(
                            "Preview the mapped rows before confirming. Rows with invalid "
                            "patterns or missing required fields are reported so you can "
                            "fix the source file or adjust mappings. Successful rows are "
                            "added to the open forecast immediately."
                        ),
                        _tip(
                            "Prepare spreadsheets with consistent column headers to speed "
                            "up mapping—you can re-use the same layout for monthly updates."
                        ),
                        _important(
                            "Import adds cash flows to the current forecast. It does not "
                            "replace existing lines unless you delete them first."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Export executive PDF"),
                    blocks=(
                        _paragraph(
                            "After you run a projection, use Export executive report on "
                            "the Projection tab to generate a polished PDF for sharing. "
                            "The report includes a monthly cash-bridge table, a balance "
                            "chart, foreign-exchange footnotes when applicable, and a "
                            "methodology appendix."
                        ),
                        _paragraph(
                            "If scenario overrides are active, the export may also include "
                            "a scenario comparison table summarizing how the scenario "
                            "run differs from the saved baseline. Export CSV is available "
                            "on the same page for spreadsheet analysis."
                        ),
                        _tip(
                            "Run the forecast immediately before exporting so the report "
                            "reflects your latest cash flows and horizon."
                        ),
                        _important(
                            "The executive report describes one forecast run. Re-export "
                            "after material changes rather than editing the PDF by hand."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Share .ftplan files"),
                    blocks=(
                        _paragraph(
                            "On the Forecasts page, each forecast card offers Export "
                            "forecast to save a versioned .ftplan bundle. The file "
                            "contains the forecast metadata, cash flows, and any exchange "
                            "rates embedded in the bundle for portability."
                        ),
                        _paragraph(
                            "Use Import forecast on the Forecasts page to create a new "
                            "forecast from a .ftplan file. This is the recommended way to "
                            "back up work, move between computers, or share a starting "
                            "point with a colleague."
                        ),
                        _tip(
                            "Keep dated .ftplan backups before large restructuring so you "
                            "can recover an earlier forecast if needed."
                        ),
                        _important(
                            "The .ftplan extension is unchanged for compatibility—user-facing "
                            "labels say Import forecast and Export forecast."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("Settings & preferences"),
            sections=(
                ManualSection(
                    heading=_translate("Theme and language"),
                    blocks=(
                        _paragraph(
                            "Open Settings from the gear icon in the app header. Under "
                            "Appearance, toggle Dark mode to switch between light and dark "
                            "themes. The change applies immediately with no restart required."
                        ),
                        _paragraph(
                            "The Language control lists English, French, Russian, Spanish, "
                            "and German. Selecting a language retranslates the entire "
                            "interface, including menus, dialogs, and export headers, in "
                            "the same session."
                        ),
                        _tip(
                            "Set language before generating shared PDF exports if recipients "
                            "expect a particular locale."
                        ),
                        _important(
                            "Language preference is stored locally in application settings "
                            "on your device."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Exchange rates"),
                    blocks=(
                        _paragraph(
                            "Exchange rates are managed globally under Data & Currency in "
                            "Settings. Expand Manage exchange rates to add or edit pairs "
                            "relative to your forecasts' base currencies. During a "
                            "projection run, each cash flow in a foreign currency converts "
                            "using the stored rate before amounts are summed."
                        ),
                        _paragraph(
                            "Enable Fetch live exchange rates to download current values "
                            "when network access is available. Attribution for the rate "
                            "provider appears on the Settings page. If a required rate is "
                            "missing, the forecast run fails with an error rather than "
                            "guessing a value."
                        ),
                        _tip(
                            "Refresh live rates before an important projection if markets "
                            "have moved significantly since your last update."
                        ),
                        _important(
                            "Exchange rates apply app-wide. Updating a rate affects every "
                            "forecast that uses the affected currency pair."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Methodology"),
                    blocks=(
                        _paragraph(
                            "The Methodology page—linked from Settings under About—explains "
                            "how Cash Flow Planner computes daily balances, detects the "
                            "first cash shortfall, expands date patterns, and normalizes "
                            "currencies. It is aimed at readers who want technical "
                            "transparency."
                        ),
                        _paragraph(
                            "This user manual focuses on day-to-day workflows; the "
                            "Methodology page complements it with calculation detail. "
                            "Executive PDF exports also include a methodology appendix "
                            "for stakeholders who receive reports."
                        ),
                        _tip(
                            "Share the Methodology page with clients or partners who ask "
                            "how projection numbers are produced."
                        ),
                    ),
                ),
            ),
        ),
        ManualChapter(
            title=_translate("Quick reference"),
            sections=(
                ManualSection(
                    heading=_translate("Date pattern cheat sheet"),
                    blocks=(
                        _paragraph(
                            "Type patterns exactly as shown in the Pattern column. "
                            "Trailing dots matter. The app validates syntax and shows a "
                            "plain-language description under the field while you edit."
                        ),
                        _pattern_table(
                            "Common date patterns",
                            (
                                ("...", "Every day (daily)"),
                                ("10..", "Monthly on the 10th"),
                                ("15.03.", "Yearly on 15 March"),
                                ("15.03.2026", "One-time on 15 March 2026"),
                            ),
                        ),
                        _tip(
                            "Monthly patterns use day-of-month before the two dots; yearly "
                            "patterns use day.month.; one-time patterns add the full year."
                        ),
                    ),
                ),
                ManualSection(
                    heading=_translate("Tips and shortcuts"),
                    blocks=(
                        _paragraph(
                            "The app shell keeps Forecasts as the home view and Settings "
                            "one click away in the header. Inside a forecast, switch "
                            "between Cash flows, Projection, and Change history using the "
                            "tabs at the top of the detail view."
                        ),
                        _bullets(
                            "Forecasts page — create, import, export, and open forecasts",
                            "Cash flows tab — add, edit, import, and organize line items",
                            "Projection tab — set horizon, run forecast, scenarios, exports",
                            "Settings — theme, language, exchange rates, methodology, user manual",
                        ),
                        _tip(
                            "Run a projection after every meaningful edit to cash flows "
                            "or rates so shortfall alerts and charts stay accurate."
                        ),
                        _important(
                            "Scenario overrides live only on the Projection tab and are "
                            "cleared when you reset the Scenario panel—they never replace "
                            "saved cash flows."
                        ),
                    ),
                ),
            ),
        ),
    )


def _register_i18n_catalog() -> None:
    """Literal translate() calls for pyside6-lupdate extraction only."""
    QCoreApplication.translate("UserManual", "User Manual")
    QCoreApplication.translate("UserManual", "Cash Flow Planner")
    QCoreApplication.translate("UserManual", "Welcome")
    QCoreApplication.translate("UserManual", "Getting started")
    QCoreApplication.translate("UserManual", "Cash flows")
    QCoreApplication.translate("UserManual", "Running a projection")
    QCoreApplication.translate("UserManual", "What-if scenarios")
    QCoreApplication.translate("UserManual", "Import & export")
    QCoreApplication.translate("UserManual", "Settings & preferences")
    QCoreApplication.translate("UserManual", "Quick reference")
    QCoreApplication.translate("UserManual", "About Cash Flow Planner")
    QCoreApplication.translate("UserManual", "Who this manual is for")
    QCoreApplication.translate("UserManual", "First launch")
    QCoreApplication.translate("UserManual", "Create a forecast")
    QCoreApplication.translate("UserManual", "Start from a template")
    QCoreApplication.translate("UserManual", "Add income and expenses")
    QCoreApplication.translate("UserManual", "Date patterns")
    QCoreApplication.translate("UserManual", "Edit and delete")
    QCoreApplication.translate("UserManual", "Set horizon and opening balance")
    QCoreApplication.translate("UserManual", "Read the monthly table")
    QCoreApplication.translate("UserManual", "Balance chart")
    QCoreApplication.translate("UserManual", "Cash shortfall alert")
    QCoreApplication.translate("UserManual", "Enable overrides")
    QCoreApplication.translate("UserManual", "Compare with baseline")
    QCoreApplication.translate("UserManual", "Import CSV/Excel")
    QCoreApplication.translate("UserManual", "Export executive PDF")
    QCoreApplication.translate("UserManual", "Share .ftplan files")
    QCoreApplication.translate("UserManual", "Theme and language")
    QCoreApplication.translate("UserManual", "Exchange rates")
    QCoreApplication.translate("UserManual", "Methodology")
    QCoreApplication.translate("UserManual", "Date pattern cheat sheet")
    QCoreApplication.translate("UserManual", "Tips and shortcuts")
    QCoreApplication.translate(
        "UserManual",
        "Cash Flow Planner is an offline-first cash-flow forecasting application for"
        + "individuals and small businesses. You define income and expense cash flows, run"
        + "projections over a chosen horizon, and review a running balance that shows when a"
        + "cash shortfall may occur.",
    )
    QCoreApplication.translate(
        "UserManual",
        "All forecasts, cash flows, and exchange rates are stored locally in a SQLite"
        + "database on your computer. The app does not require an account, sign-in, or"
        + "continuous internet connection to build and run forecasts.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Your data never leaves your device unless you explicitly export a file or share a"
        + "backup.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Cash Flow Planner does not provide automatic cloud backup. Use Export forecast to"
        + "save a .ftplan file if you need a portable copy of your work.",
    )
    QCoreApplication.translate(
        "UserManual",
        "This manual is written for freelancers, business operators, fractional CFOs, and"
        + "advisors who need a practical cash-flow forecast without enterprise complexity."
        + "Whether you manage personal income swings or a small company's payroll and vendor"
        + "payments, the same workflow applies.",
    )
    QCoreApplication.translate(
        "UserManual", "Build a forecast from scratch or start from a bundled template"
    )
    QCoreApplication.translate(
        "UserManual", "Model recurring and one-time cash flows with compact date patterns"
    )
    QCoreApplication.translate(
        "UserManual", "Run projections and spot the first cash shortfall before it happens"
    )
    QCoreApplication.translate(
        "UserManual", "Explore scenarios without overwriting saved cash flows"
    )
    QCoreApplication.translate(
        "UserManual",
        "Throughout the app, user-facing text uses professional forecasting"
        + "vocabulary—Forecast, Cash flow, Cash shortfall, and Scenario—rather than"
        + "personal-finance jargon.",
    )
    QCoreApplication.translate(
        "UserManual",
        "When you launch Cash Flow Planner for the first time, the Forecasts page is empty."
        + "The app creates a local database automatically in your platform application-data"
        + "folder, so you can start working immediately.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The main navigation shell keeps Forecasts as your home view. Open Settings from"
        + "the gear icon in the app header to adjust appearance and language before you"
        + "create your first forecast.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Switch Dark mode and Language in Settings without restarting the application—the"
        + "interface updates live.",
    )
    QCoreApplication.translate(
        "UserManual",
        "If you reinstall the app on the same machine, your existing database is preserved"
        + "in the application-data location.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Select New forecast on the Forecasts page. A dialog asks whether to start with a"
        + "blank forecast or use a template. For a blank forecast, enter a descriptive name,"
        + "choose the forecast base currency, and set the opening cash balance.",
    )
    QCoreApplication.translate(
        "UserManual",
        "After creation, the forecast detail view opens with three tabs: Cash flows,"
        + "Projection, and Change history. Add cash flows on the first tab, then move to"
        + "Projection when you are ready to run a forecast.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Pick the base currency carefully—it is the currency used to sum cash flows during"
        + "a projection run. Other currencies convert using exchange rates from Settings.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Each forecast is independent. Deleting a forecast removes its cash flows and"
        + "projection history for that forecast only.",
    )
    QCoreApplication.translate(
        "UserManual",
        "When you choose From template in the New forecast dialog, the template picker"
        + "lists bundled starting points such as freelancer, small business, and household"
        + "cash-flow examples. Each card shows a short description of what the template"
        + "includes.",
    )
    QCoreApplication.translate(
        "UserManual",
        "After you select a template and confirm a forecast name, Cash Flow Planner creates"
        + "the forecast and pre-fills typical income and expense cash flows. Every line item"
        + "remains fully editable—templates are a shortcut, not a constraint.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Templates are ideal for onboarding: review each pre-filled cash flow, adjust"
        + "amounts to match your situation, and delete lines you do not need.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Choosing a template does not lock currency or patterns. You can change any field"
        + "immediately after creation.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Open a forecast and select the Cash flows tab. Income and expense cash flows are"
        + "listed separately so you can scan inflows and outflows at a glance. Use the Add"
        + "cash flow floating action button to open the cash flow drawer.",
    )
    QCoreApplication.translate(
        "UserManual",
        "In the drawer, choose whether the line is income or expense, enter a name and"
        + "amount, pick a currency, and type a date pattern. The pattern preview label below"
        + "the field updates as you type so you can confirm the schedule before saving.",
    )
    QCoreApplication.translate(
        "UserManual", "Income cash flows increase your balance on scheduled dates"
    )
    QCoreApplication.translate(
        "UserManual", "Expense cash flows decrease your balance on scheduled dates"
    )
    QCoreApplication.translate(
        "UserManual", "Use Import on the Cash flows page to load rows from CSV or Excel"
    )
    QCoreApplication.translate(
        "UserManual",
        "Give each cash flow a clear name—projection results and the cash shortfall banner"
        + "reference these names when highlighting contributing line items.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Every cash flow is scheduled with a compact date pattern instead of picking"
        + "individual calendar dates. Patterns can represent daily, monthly, yearly, or"
        + "one-time events. The syntax is validated while you edit, and invalid patterns show"
        + "an error before you save.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Examples include ... for every day, 10.. for monthly on the 10th, 15.03. for"
        + "yearly on 15 March, and 15.03.2026 for a single occurrence. The live description"
        + "under the pattern field restates the schedule in plain language.",
    )
    QCoreApplication.translate(
        "UserManual",
        "If a pattern looks wrong, check the preview label before saving—a small typo can"
        + "shift every occurrence in the projection range.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The Quick reference chapter at the end of this manual lists common patterns in a"
        + "cheat sheet table.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Tap or click a cash flow in the list to reopen the drawer in Edit cash flow mode."
        + "Changes save to the forecast immediately when you confirm. Amount, currency,"
        + "pattern, and active state can all be updated.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Use delete inside the drawer to remove a cash flow you no longer need. After any"
        + "edit, return to the Projection tab and run the forecast again so monthly summaries"
        + "and the balance chart reflect your latest data.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Deactivate a line item temporarily using the Scenario panel on the Projection tab"
        + "if you only want to test removing it.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Edits on the Cash flows tab are saved permanently to your forecast. Scenario"
        + "overrides on the Projection tab are not.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Select the Projection tab to configure and run a forecast. Choose the projection"
        + "start date, end date (horizon), and confirm the opening cash balance. The controls"
        + "at the top of the page apply to the current forecast run.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Press Run forecast to expand every active cash flow across the date range, convert"
        + "foreign currencies to the forecast base currency, and compute a day-by-day running"
        + "balance. While the run is in progress, the button shows a busy state.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Re-run the forecast after you change cash flows, exchange rates, or the horizon so"
        + "tables and charts stay current.",
    )
    QCoreApplication.translate(
        "UserManual",
        "If a required exchange rate is missing, the run stops with a clear error—add the"
        + "rate in Settings and try again.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Below the controls, the monthly table aggregates each month in the projection"
        + "range. Columns typically include opening balance, inflows, outflows, net flow, and"
        + "closing balance. Amounts use semantic coloring—inflows in green and outflows in"
        + "red—so trends are easy to scan.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Months where the closing balance falls below zero are treated as a cash shortfall."
        + "Those rows receive an amber highlight so you can spot problem periods without"
        + "reading every number.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Compare consecutive months to see whether a shortfall is a one-month timing gap or"
        + "a sustained cash-flow problem.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The table shows monthly snapshots. The cash shortfall banner reports the first day"
        + "the daily balance drops below zero, which may fall mid-month.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The balance chart plots your running balance across the projection horizon. The"
        + "area above zero uses the primary brand color; when the balance drops below zero,"
        + "the chart fills the deficit region in red so shortfalls stand out visually.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Move the pointer over the chart to show a vertical guide line, the nearest data"
        + "point, and a tooltip with the date and balance for that day. This is useful for"
        + "pinpointing when a decline begins.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Use the chart together with the monthly table—the chart shows timing within a"
        + "month; the table summarizes totals.",
    )
    QCoreApplication.translate(
        "UserManual",
        "When a projection finds a day with a negative closing balance, a dismissible cash"
        + "shortfall banner appears at the top of the Projection tab. It names the first"
        + "shortfall date and the expense cash flow that contributed on that day.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Address a shortfall by adjusting timing or amounts on the Cash flows tab, adding"
        + "income, or opening the Scenario panel to test changes before you commit them."
        + "Dismiss the banner when you have noted the date—it reappears on the next run if"
        + "the shortfall still exists.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Only the earliest cash shortfall in a run is reported. Later shortfalls during the"
        + "same projection are not listed separately.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Export an executive report after a run to share projection results, including the"
        + "balance chart, with stakeholders.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The Scenario panel on the Projection tab lets you explore what-if changes without"
        + "altering saved cash flows. Expand the panel to see each active line item with"
        + "override controls for amount and whether the line is active in the current run.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Adjust an amount or deactivate a line, then run the forecast again. The projection"
        + "engine applies overrides only for that run, leaving your stored forecast unchanged"
        + "on the Cash flows tab.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Use scenarios to test hiring, deferring a payment, or pausing a subscription"
        + "before you edit the baseline forecast.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Scenario overrides are never saved to your forecast. Clear overrides or close the"
        + "panel to return to the saved baseline.",
    )
    QCoreApplication.translate(
        "UserManual",
        "After you enable overrides, run the forecast to see updated monthly balances,"
        + "chart shape, and cash shortfall timing. Compare the results mentally with your"
        + "last baseline run, or note which line items you changed in the Scenario panel.",
    )
    QCoreApplication.translate(
        "UserManual",
        "When you export an executive report while overrides are active, the PDF can"
        + "include a scenario comparison section that contrasts key metrics between the"
        + "baseline and the current scenario run.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Toggle overrides off line by line to isolate which change moved the first cash"
        + "shortfall date.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Change history on the forecast detail tab records edits to saved cash flows, not"
        + "temporary scenario overrides.",
    )
    QCoreApplication.translate(
        "UserManual",
        "On the Cash flows tab, select Import to open the import dialog. Choose a CSV or"
        + "Excel file from your computer and map file columns to name, amount, type (income"
        + "or expense), currency, and date pattern.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Preview the mapped rows before confirming. Rows with invalid patterns or missing"
        + "required fields are reported so you can fix the source file or adjust mappings."
        + "Successful rows are added to the open forecast immediately.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Prepare spreadsheets with consistent column headers to speed up mapping—you can"
        + "re-use the same layout for monthly updates.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Import adds cash flows to the current forecast. It does not replace existing lines"
        + "unless you delete them first.",
    )
    QCoreApplication.translate(
        "UserManual",
        "After you run a projection, use Export executive report on the Projection tab to"
        + "generate a polished PDF for sharing. The report includes a monthly cash-bridge"
        + "table, a balance chart, foreign-exchange footnotes when applicable, and a"
        + "methodology appendix.",
    )
    QCoreApplication.translate(
        "UserManual",
        "If scenario overrides are active, the export may also include a scenario"
        + "comparison table summarizing how the scenario run differs from the saved baseline."
        + "Export CSV is available on the same page for spreadsheet analysis.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Run the forecast immediately before exporting so the report reflects your latest"
        + "cash flows and horizon.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The executive report describes one forecast run. Re-export after material changes"
        + "rather than editing the PDF by hand.",
    )
    QCoreApplication.translate(
        "UserManual",
        "On the Forecasts page, each forecast card offers Export forecast to save a"
        + "versioned .ftplan bundle. The file contains the forecast metadata, cash flows, and"
        + "any exchange rates embedded in the bundle for portability.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Use Import forecast on the Forecasts page to create a new forecast from a .ftplan"
        + "file. This is the recommended way to back up work, move between computers, or"
        + "share a starting point with a colleague.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Keep dated .ftplan backups before large restructuring so you can recover an"
        + "earlier forecast if needed.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The .ftplan extension is unchanged for compatibility—user-facing labels say Import"
        + "forecast and Export forecast.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Open Settings from the gear icon in the app header. Under Appearance, toggle Dark"
        + "mode to switch between light and dark themes. The change applies immediately with"
        + "no restart required.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The Language control lists English, French, Russian, Spanish, and German."
        + "Selecting a language retranslates the entire interface, including menus, dialogs,"
        + "and export headers, in the same session.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Set language before generating shared PDF exports if recipients expect a"
        + "particular locale.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Language preference is stored locally in application settings on your device.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Exchange rates are managed globally under Data & Currency in Settings. Expand"
        + "Manage exchange rates to add or edit pairs relative to your forecasts' base"
        + "currencies. During a projection run, each cash flow in a foreign currency converts"
        + "using the stored rate before amounts are summed.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Enable Fetch live exchange rates to download current values when network access is"
        + "available. Attribution for the rate provider appears on the Settings page. If a"
        + "required rate is missing, the forecast run fails with an error rather than"
        + "guessing a value.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Refresh live rates before an important projection if markets have moved"
        + "significantly since your last update.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Exchange rates apply app-wide. Updating a rate affects every forecast that uses"
        + "the affected currency pair.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The Methodology page—linked from Settings under About—explains how Cash Flow"
        + "Planner computes daily balances, detects the first cash shortfall, expands date"
        + "patterns, and normalizes currencies. It is aimed at readers who want technical"
        + "transparency.",
    )
    QCoreApplication.translate(
        "UserManual",
        "This user manual focuses on day-to-day workflows; the Methodology page complements"
        + "it with calculation detail. Executive PDF exports also include a methodology"
        + "appendix for stakeholders who receive reports.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Share the Methodology page with clients or partners who ask how projection numbers"
        + "are produced.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Type patterns exactly as shown in the Pattern column. Trailing dots matter. The"
        + "app validates syntax and shows a plain-language description under the field while"
        + "you edit.",
    )
    QCoreApplication.translate("UserManual", "Common date patterns")
    QCoreApplication.translate(
        "UserManual",
        "Monthly patterns use day-of-month before the two dots; yearly patterns use"
        + "day.month.; one-time patterns add the full year.",
    )
    QCoreApplication.translate(
        "UserManual",
        "The app shell keeps Forecasts as the home view and Settings one click away in the"
        + "header. Inside a forecast, switch between Cash flows, Projection, and Change"
        + "history using the tabs at the top of the detail view.",
    )
    QCoreApplication.translate(
        "UserManual", "Forecasts page — create, import, export, and open forecasts"
    )
    QCoreApplication.translate(
        "UserManual", "Cash flows tab — add, edit, import, and organize line items"
    )
    QCoreApplication.translate(
        "UserManual", "Projection tab — set horizon, run forecast, scenarios, exports"
    )
    QCoreApplication.translate(
        "UserManual", "Settings — theme, language, exchange rates, methodology, user manual"
    )
    QCoreApplication.translate(
        "UserManual",
        "Run a projection after every meaningful edit to cash flows or rates so shortfall"
        + "alerts and charts stay accurate.",
    )
    QCoreApplication.translate(
        "UserManual",
        "Scenario overrides live only on the Projection tab and are cleared when you reset"
        + "the Scenario panel—they never replace saved cash flows.",
    )
    QCoreApplication.translate("UserManual", "Every day (daily)")
    QCoreApplication.translate("UserManual", "Monthly on the 10th")
    QCoreApplication.translate("UserManual", "Yearly on 15 March")
    QCoreApplication.translate("UserManual", "One-time on 15 March 2026")

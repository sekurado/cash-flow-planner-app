#!/usr/bin/env python3
"""Generate bundled user-manual PDF artifacts for Cash Flow Planner.

Bootstraps a minimal Qt application so ``QCoreApplication.translate`` resolves
manual strings, then writes PDFs via ``ManualPdfExporter``.

Usage:
    python scripts/generate_manual.py
    python scripts/generate_manual.py --locale en
    python scripts/generate_manual.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QCoreApplication, QTranslator  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from src.app.identity import APPLICATION_NAME, ORGANIZATION_NAME  # noqa: E402
from src.export.manual_pdf_exporter import ManualPdfExporter  # noqa: E402

_SUPPORTED_LOCALES = ("en", "fr", "ru", "es", "de")
_DEFAULT_LOCALE = "en"
_active_translator: QTranslator | None = None


def _bootstrap_qt(locale: str) -> QCoreApplication:
    global _active_translator

    QCoreApplication.setOrganizationName(ORGANIZATION_NAME)
    QCoreApplication.setApplicationName(APPLICATION_NAME)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    if _active_translator is not None:
        app.removeTranslator(_active_translator)
        _active_translator = None

    if locale != _DEFAULT_LOCALE:
        translator = QTranslator(app)
        qm_path = ROOT / "resources" / "i18n" / f"app_{locale}.qm"
        if qm_path.is_file() and translator.load(str(qm_path)):
            app.installTranslator(translator)
            _active_translator = translator

    return app


def _output_paths(locale: str) -> tuple[Path, Path]:
    filename = f"CashFlowPlanner-UserManual_{locale}.pdf"
    return (
        ROOT / "resources" / "manual" / filename,
        ROOT / "docs" / "manual" / filename,
    )


def generate_manual(locale: str) -> tuple[Path, Path]:
    _bootstrap_qt(locale)
    bundled_path, docs_path = _output_paths(locale)
    bundled_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    exporter = ManualPdfExporter()
    exporter.export(bundled_path, locale=locale)
    docs_path.write_bytes(bundled_path.read_bytes())
    return bundled_path, docs_path


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Cash Flow Planner user-manual PDFs")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--locale",
        choices=_SUPPORTED_LOCALES,
        default=_DEFAULT_LOCALE,
        help="Locale to generate (default: en)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Generate every supported locale (en, fr, ru, es, de)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    locales = _SUPPORTED_LOCALES if args.all else (args.locale,)

    for locale in locales:
        bundled_path, docs_path = generate_manual(locale)
        print(f"Wrote {bundled_path}")
        print(f"Wrote {docs_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

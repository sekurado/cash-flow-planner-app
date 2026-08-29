# Receipt OCR — Spike & Provider Strategy

This document records the **Story 33 spike** for receipt-assisted expense entry. It defines how
Cash Flow Planner will turn receipt photos into **suggested** form fields. OCR is **assistive
only**: the user always reviews and confirms before a recorded expense is saved. There is no
silent auto-import.

Related: [Story 33 — Receipt-Assisted Expense Entry](https://github.com/sekurado/cash-flow-planner-app/issues/4),
`src/domain/receipt_ocr.py` (`ReceiptOcrProvider`, `ReceiptOcrResult`).

---

## Product constraints

| Constraint | Implication |
|------------|-------------|
| **NFR-01 offline-first** | Tier A (on-device OCR) is the default path; cloud OCR is opt-in only. |
| **Assistive UX** | OCR suggests amount, date, and merchant/name; user edits and taps Save. |
| **No receipt schema** | Raw OCR yields lines of text; a separate **heuristic parser** (Task 33_3) maps lines to fields. |
| **Background work** | OCR runs in a `QRunnable` worker; ViewModel surfaces errors via `error` Q_PROPERTY. |

---

## Why generic OCR alone is insufficient

Phone-camera photos of thermal receipts are hard for off-the-shelf OCR:

| Issue | Effect |
|-------|--------|
| Fade / low contrast | Character confusions (`0`/`O`, `1`/`7`) |
| Skew, curl, shadows | Broken line order, merged columns |
| Logos, QR blocks | Noise in the middle of totals |
| Multi-column layout | Amount not tied to the right line |
| No receipt schema | Blob of text, not `{total, date, merchant}` |

The product problem is **field extraction + confidence UI**, not only character recognition.

---

## Tiered approach

### Tier A — Ship first (offline, realistic)

1. **Store receipt image** under `AppDataLocation/receipts/` (Task 33_2); DB holds relative path.
2. **Platform-native OCR** where available (usually better than Tesseract on macOS photos):
   - **macOS:** Vision framework (`VNRecognizeTextRequest`) via PyObjC or a thin native helper.
   - **Windows:** `Windows.Media.Ocr` via WinRT bindings (feasibility to validate in Task 33_3).
   - **Linux:** optional Tesseract with preprocessing — **best-effort only**; clear “limited support” copy.
3. **Heuristic parser** (pure Python, Task 33_3): total keywords, date regex, merchant = first plausible line.
4. **Review screen** (Task 33_4): thumbnail + editable fields + low-confidence badges → existing `RecordedExpenseService.create`.

### Tier B — Optional online (Settings toggle, off by default)

- Cloud document APIs (Google Document AI, Azure Form Recognizer, AWS Textract) behind the same
  `ReceiptOcrProvider` protocol.
- Same review UI; privacy note in Settings when enabled.

### Tier C — Defer

- Bundled on-device ML models (large downloads, maintenance).
- Full line-item / SKU extraction.

**Avoid as the only solution:** Tesseract alone on JPEG receipt photos (acceptable only as a
documented Linux fallback).

---

## Platform matrix (v1 target)

| Platform | Tier A provider | Expected quality | Ship note |
|----------|-----------------|------------------|-----------|
| **macOS** | Vision (`VNRecognizeTextRequest`) | Good | **Minimum v1 implementation** (Task 33_3) |
| **Windows** | `Windows.Media.Ocr` | Medium–good | Spike in 33_3; stub with clear message if blocked |
| **Linux** | Tesseract + preprocessing | Poor–medium | Best-effort; unsupported message when missing deps |
| **All** | Cloud provider (Tier B) | High | Optional; off by default |

---

## Provider interface

Defined in `src/domain/receipt_ocr.py` (pure Python, no Qt):

```python
class ReceiptOcrProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def extract_text(self, image_path: Path) -> ReceiptOcrResult: ...
```

`ReceiptOcrResult` contains:

- `lines: tuple[ReceiptOcrLine, ...]` — each line has `text` and `confidence` in `[0, 1]`.
- `provider_id: str` — e.g. `vision-macos`, `winrt-ocr`, `tesseract`, `cloud-document-ai`.
- `overall_confidence: float` — aggregate score for the review UI (mean of line confidences unless the provider supplies a better signal).

Implementations live under `src/integrations/receipt_ocr/`. The domain protocol stays stable so
unit tests can mock OCR without loading native libraries.

**Errors:** `ReceiptOcrUnavailableError` (platform unsupported), `ReceiptOcrError` (bad file /
processing failure).

---

## PyInstaller / packaging impact

| Component | Bundle impact | Mitigation |
|-----------|---------------|------------|
| **macOS Vision** | PyObjC + Vision frameworks linked at runtime | Document in `docs/BUILD.md` (Task 33_5); gate import so dev runs without PyObjC on other OSes |
| **Windows WinRT OCR** | WinRT bindings; Windows-only | Optional extra in `pyproject.toml` extras; exclude from macOS/Linux CI |
| **Tesseract (Linux)** | **Do not bundle** Tesseract in the app | Require system `tesseract` package or disable OCR with explanatory UI |
| **Cloud OCR (Tier B)** | `httpx` already used for exchange rates | No new binary deps; API keys via Settings / env, never committed |

PyInstaller one-folder builds should **lazy-import** platform providers so Linux/Windows CI does not
pull macOS-only frameworks. Follow the pattern used for optional network features in
`exchange_rate_fetcher.py`.

---

## Accuracy expectations (manual spike)

Formal accuracy testing with real receipts is **out of scope** for Task 33_1. For implementation
planning, assume:

- **macOS Vision:** usable suggestions on ~70–90% of clear photos; totals and dates often need one edit.
- **Linux Tesseract:** frequent failures on thermal paper; treat as fallback only.
- **All tiers:** merchant/name suggestion is weak; always editable.

Task 33_3 may add anonymized fixture images and parser-only tests (text blobs, no image dependency in CI).

---

## Task map (Story 33)

| Task | Deliverable |
|------|-------------|
| **33_1** (this doc) | `docs/receipt-ocr.md` + `ReceiptOcrProvider` protocol |
| 33_2 | Receipt file storage + schema column |
| 33_3 | macOS Vision provider + `ReceiptFieldParser` + `ReceiptOcrWorker` |
| 33_4 | Review UI + `QRunnable` wiring |
| 33_5 | Tests, i18n, DESIGN.md **FR-27**, BUILD.md native deps |

### Task 33_3 implementation notes

- **Parser:** `src/domain/receipt_field_parser.py` (`ReceiptFieldParser`) maps OCR lines to
  amount / date / merchant hints with per-field confidence. Unit tests use fixture text blobs
  (`tests/unit/test_receipt_field_parser.py`) — no images in CI.
- **macOS:** `MacosVisionOcrProvider` lazy-imports PyObjC Vision. Install extra `ocr-macos` for
  source runs. Missing PyObjC raises `ReceiptOcrUnavailableError`.
- **Windows / Linux:** `UnsupportedReceiptOcrProvider` raises `ReceiptOcrUnavailableError` with a
  clear manual-entry message. WinRT OCR was evaluated and **stubbed for v1** (packaging + CI cost;
  revisit in a later story).
- **Worker:** `src/app/workers/receipt_ocr_worker.py` runs `extract_text` + `parse` on a
  `QRunnable` and emits a JSON-ready dict. ViewModel / QML wiring is Task 33_4.
- **Factory:** `create_receipt_ocr_provider()` / `receipt_ocr_is_available()` in
  `src/integrations/receipt_ocr/`.

---

## Open decisions (for later tasks)

- **Camera capture** vs file picker only in v1 (file picker first).
- **PyObjC** vs small Swift/ObjC helper binary for Vision.
- **Windows/Linux stubs:** disable “Scan receipt” button vs show dialog explaining limited support
  (provider already raises `ReceiptOcrUnavailableError`; 33_4 chooses the UI).

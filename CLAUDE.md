# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a BJT (Business Japanese Test / ビジネス日本語能力テスト) self-study application. It targets Vietnamese learners preparing for the BJT exam. All UI text is in Vietnamese.

## Running the App

Open `index.html` directly in a browser — no build step, no server required. It is a fully self-contained single-file app.

`BJT_Flashcard_912tu.html` is embedded as an `<iframe>` inside the Flashcard tab of `index.html`.

## Architecture

### `index.html` (~4750 lines)
The entire application lives here — CSS, HTML markup, and JavaScript all in one file. Key sections:

- **Navigation tabs** (`showSection(name)`): `roadmap`, `grammar`, `flashcard`, `flashcard912`, `matchgame`, `search`, `reading`, `reference`, `mocktest`. `showSection` relies on the global `event.target`, so nav buttons must not contain child elements that could receive the click (e.g. a `<span class="badge">`).
- **`grammarData`** (JS object): Grammar rules organized by category, rendered dynamically
- **`flashcardData`** (JS object): Vocabulary cards grouped by category (e.g., Văn phòng, Chức vụ, Keigo…). Each card has `word`, `reading`, `meaning`, and optionally `explain`, `example`, `exampleReading`
- **Mock test engine**: Questions stored in `testQuestions` array with `part`, `section`, `audio`, `context`, `question`, `options`, `answer`, `explain` fields. Scoring maps to BJT levels J1–J5 (200–800 scale)
- **`playAudio(btn, src)`**: Plays MP3/WMA files from the local directory structure

### `BJT_Flashcard_912tu.html` (~614 lines)
Standalone flashcard viewer for 912 vocabulary items, embedded as iframe. Loads `vocab_912.js` (`var VOCAB = {J5:[...], ...}`).

### `BJT_Match_Game.html`
Standalone vocabulary matching game ("Ghép từ" tab, embedded as iframe; also works opened directly). Two 3×3 grids (words | meanings), played lesson by lesson (Bài 1–45, shuffled within a lesson, loops back to Bài 1), with score/combo/mistakes, per-round + total timer, hint (example sentences) and a "review wrong words" mode. Progress is persisted in `localStorage` under the key `bjt_match_v1` (the only localStorage use in the app). `?lesson=N` in the URL jumps straight into lesson N (for testing). Loads `vocab_thaole.js`.

### `vocab_thaole.js` (generated — do not hand-edit)
`var THAOLE_META = {...}; var THAOLE_VOCAB = [{id, n, lesson, pdfNo, word, alt, reading, en, meaning, short, suru, pos, tag, examples:[{ja, vi}], note}, ...]` — 2212 words from the 45-lesson Thaolejp PDF. `id` is a global sequential index (PDF numbering has gaps/duplicates); `short` is the trimmed meaning shown on game tiles.

### `extract_thaole_vocab.py`
Regenerates `vocab_thaole.js` from `Thaolejp_BJT_Chinh phuc tu vung (kem dich nghia).pdf` using poppler's `pdftotext` (`brew install poppler`). Prints a review report (lessons ≠ 50 words, missing meanings, inline Vietnamese headers, marker residue, truncated shorts). Hand corrections go in the `OVERRIDES` dict keyed by `(lesson, pdfNo)` so they survive re-runs. Run with:
```
python3 extract_thaole_vocab.py
```

### `update_flashcards.py`
Python utility to batch-update flashcard entries in `index.html` via regex. Hardcodes the file path `/Users/tranmanh/Desktop/LEARN/bjt/BJT_Learning_Hub.html` — update the path if the file is renamed. Run with:
```
python3 update_flashcards.py
```

### `bjt_vocab_extracted.json`
Source vocabulary data (451 words across 14 categories) extracted from the PDF study materials.

## Data Files

- `BJT_Tu_vung_1000tu.xlsx` — vocabulary spreadsheet (source data)
- `Lo_trinh_hoc_BJT_8_tuan.docx` — 8-week study roadmap
- `VOCABULARY_SUMMARY.txt` — extraction report documenting which PDFs were processed and vocabulary counts per category
- `Thaolejp_BJT_Chinh phuc tu vung (kem dich nghia).pdf` — source of `vocab_thaole.js` (45 lessons, ~50 words each)
- Audio: `QUYỂN 1/` contains `.wma` files; `QUYỂN 4/` contains `.mp3` files

## Editing Flashcard Data

Vocabulary cards in `flashcardData` inside `index.html` follow this shape:
```js
{ word: "単語", reading: "たんご", meaning: "từ vựng", explain: "...", example: "...", exampleReading: "..." }
```
The `explain`, `example`, and `exampleReading` fields are optional but preferred for Văn bản thương mại entries. Use `update_flashcards.py` as a template for bulk updates.

# Transformation Figures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four evidence-bearing figures that explain source hashing, fusion, conditioning, and rejection sampling.

**Architecture:** Extend the transformation payload with a compact raw-byte preview, then render all figures with small browser helpers using inline SVG and DOM cells. Preserve existing exact hexadecimal and numeric values as direct labels and fallbacks.

**Tech Stack:** Python, pytest, vanilla JavaScript, inline SVG, CSS

---

### Task 1: Transformation Payload

**Files:**
- Modify: `tests/unit/test_web_visuals.py`
- Modify: `src/randomiser/trace/web_visuals.py`

- [ ] Add a failing assertion that each `sourceHashes` item includes the exact first sixteen source bytes in `rawPreview`.
- [ ] Run `pytest tests/unit/test_web_visuals.py::test_transformation_visual_matches_pipeline_otp -q` and confirm it fails for missing `rawPreview`.
- [ ] Add `rawPreview` while building accepted source-hash items.
- [ ] Run `pytest tests/unit/test_web_visuals.py -q` and confirm it passes.

### Task 2: Browser Figures

**Files:**
- Modify: `apps/web/static/app.js`

- [ ] Add helpers for parsing digest bytes, rendering byte strips and 8 by 8 heatmaps, drawing fusion convergence SVG, and drawing rejection-sampling SVG.
- [ ] Update `renderTransformation` so Figures 3.1 through 3.4 contain the new visuals while preserving exact text values.
- [ ] Run `node --check apps/web/static/app.js`.

### Task 3: Newsprint Figure Styling

**Files:**
- Modify: `apps/web/static/css/app.css`

- [ ] Style byte cells, source transformations, SVG diagrams, direct labels, and mobile stacking using the existing Newsprint palette.
- [ ] Confirm the figures have text alternatives and do not rely on hover.

### Task 4: Documentation And Verification

**Files:**
- Modify: `wording_done.txt`

- [ ] Record what figures were added and why.
- [ ] Run `pytest -q`.
- [ ] Run JavaScript and Python syntax checks.
- [ ] Start the local web app and inspect transformation focus on desktop and mobile.
- [ ] Remove temporary QA screenshots and stop the QA server.


# Educational Web Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a streamed, newsprint-style educational web report that permanently saves and explains every source capture and OTP transformation.

**Architecture:** Retain exact source evidence on each source object, add an optional stage observer to the existing entropy manager, and build preview/chart payloads in a focused trace helper. Node streams Python events with SSE and serves saved experiment artifacts. The static frontend renders the report with SVG figures and Web Audio playback.

**Tech Stack:** Python, NumPy, OpenCV, standard-library WAV writing, Node HTTP/SSE, vanilla HTML/CSS/JavaScript, SVG, Web Audio API.

---

### Task 1: Retain Exact Source Evidence

**Files:**
- Modify: `src/randomiser/sources/camera_source.py`
- Modify: `src/randomiser/sources/microphone_source.py`
- Modify: `src/randomiser/sources/cpu_jitter_source.py`
- Modify: `src/randomiser/sources/scheduler_jitter_source.py`
- Test: `tests/unit/test_camera_source.py`
- Test: `tests/unit/test_microphone_source.py`
- Test: `tests/unit/test_cpu_jitter_source.py`
- Test: `tests/unit/test_scheduler_jitter_source.py`

- [ ] Add failing assertions for `last_frame`, `last_samples`, `last_deltas`, and `last_thread_deltas`.
- [ ] Run the four source tests and confirm the new assertions fail.
- [ ] Retain the exact arrays and timing lists during collection without changing entropy bytes.
- [ ] Run the four source tests and confirm they pass.

### Task 2: Emit Real Pipeline Stage Events

**Files:**
- Modify: `src/randomiser/pipeline/entropy_manager.py`
- Create: `tests/unit/test_entropy_manager_observer.py`

- [ ] Write a failing test that passes an observer and expects collection, analysis, health, fusion, conditioning, and OTP stage events.
- [ ] Run the observer test and confirm it fails because the observer argument is unsupported.
- [ ] Add an optional observer callback and emit events only after each backend stage completes.
- [ ] Run the observer test and existing manager integrations.

### Task 3: Persist and Describe Preview Evidence

**Files:**
- Create: `src/randomiser/trace/web_visuals.py`
- Modify: `src/randomiser/trace/__init__.py`
- Create: `tests/unit/test_web_visuals.py`

- [ ] Write failing tests for byte series, histogram, lag pairs, camera preview files, microphone WAV, and digest explanation.
- [ ] Run the tests and confirm the helper module is missing.
- [ ] Implement compact JSON-safe chart payloads and permanent preview writers.
- [ ] Run the helper tests and confirm they pass.

### Task 4: Stream the Web Run

**Files:**
- Modify: `apps/web/web_api.py`
- Modify: `apps/web/server.js`

- [ ] Connect the manager observer to JSON event output.
- [ ] Save exact source previews after collection.
- [ ] Include artifact URLs, source visualizations, hashes, fused digest, conditioned digest, and rejection candidate in the final payload.
- [ ] Add `/api/run-stream` SSE and safe `/artifacts/` static serving.
- [ ] Verify one real streamed run saves JPG/PNG/WAV previews and emits ordered events.

### Task 5: Rebuild the Educational Newsprint Page

**Files:**
- Modify: `apps/web/index.html`
- Modify: `apps/web/static/app.js`
- Modify: `apps/web/static/css/app.css`

- [ ] Replace the kinetic dark layout with the approved newsprint report structure.
- [ ] Render live stage progress, camera transformations, audio controls, timing figures, health figures, hashing/fusion figures, and final OTP.
- [ ] Implement SVG line, histogram, threshold, scatter, and digest-flow figures with direct labels and accessible captions.
- [ ] Implement Web Audio playback speeds from 0.01x to 2x.
- [ ] Add mobile single-column layout, sharp borders, edition metadata, ticker, and inverted process section.

### Task 6: Verify and Record

**Files:**
- Modify: `apps/web/README.md`
- Modify: `wording_done.txt`

- [ ] Run Node and Python syntax checks.
- [ ] Run a real hardware streamed web run and verify preview files.
- [ ] Inspect desktop and mobile completed-flow screenshots.
- [ ] Run `pytest -q`.
- [ ] Run the source metadata scan.
- [ ] Record the redesign work and verification in `wording_done.txt`.

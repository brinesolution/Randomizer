# Educational Web Flow Design

## Goal

Turn web mode into a newsprint-style educational report that shows how real laptop source captures become entropy bytes, pass health checks, become hashes, fuse, condition, and produce a six-digit OTP.

## Source Evidence

- Camera: save the exact captured color frame, grayscale conversion, and extracted low-bit map.
- Microphone: collect one second in web mode, save the exact WAV recording, provide playback from 0.01x to 2x, and show original and extracted waveforms.
- CPU jitter: show measured timing deltas, low-byte extraction, and distribution.
- Scheduler jitter: show per-thread timing lanes, combined low-byte stream, and distribution.

All preview artifacts use the run ID and are saved under:

```text
data/experiments/<experiment_id>/output/previews/
```

## Live Process

Node exposes a server-sent events endpoint. Python emits events after real pipeline stages finish:

1. source collection
2. feature extraction and source analysis
3. health gate
4. hashing and HG-MSEF fusion
5. conditioning
6. rejection sampling and OTP generation
7. experiment save

The browser automatically reveals the relevant report section as each event arrives.

## Educational Figures

Small SVG figures use direct labels and nearby values:

- line charts for timing and waveforms
- byte-frequency histograms
- health threshold bars
- lag-1 byte-pair plots
- digest columns and a converging fusion diagram

Essential values remain visible without hover. Figures include captions and text explanations.

## Visual System

Follow `web_design.txt` strictly:

- permanent light newsprint palette
- Playfair Display headlines, Lora body text, Inter UI labels, JetBrains Mono data
- sharp black grid borders and zero radius
- dense asymmetric editorial columns
- red used sparingly for status, CTA, and emphasis
- paper texture, edition metadata, ticker, figure captions, and one inverted process section
- responsive single-column mobile layout

## Error Handling

Collection failures appear as failed source reports while the run continues when degraded-mode requirements permit it. Streaming errors show a visible report notice. Saved experiment paths remain visible after successful runs.

## Verification

- Unit tests cover retained source evidence, observer stage events, preview persistence, and visualization payloads.
- Real hardware API run verifies camera and microphone previews.
- Browser screenshots verify desktop and mobile newsprint layout and completed-flow figures.
- Full test suite and metadata scan must pass.

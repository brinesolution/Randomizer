const startButton = document.querySelector("#startButton");
const statusBadge = document.querySelector("#statusBadge");
const stageRail = document.querySelector("#stageRail");
const reportNotice = document.querySelector("#reportNotice");
const sourceGrid = document.querySelector("#sourceGrid");
const healthGrid = document.querySelector("#healthGrid");
const transformationReport = document.querySelector("#transformationReport");
const seedValue = document.querySelector("#seedValue");
const outputChoices = document.querySelector("#outputChoices");
const outputResult = document.querySelector("#outputResult");
const savePanel = document.querySelector("#savePanel");

let eventSource = null;
let audioContext = null;
let activeAudioSource = null;
const audioBuffers = new Map();
let currentRun = null;

document.querySelector("#editionDate").textContent = new Intl.DateTimeFormat("en-US", {
  dateStyle: "long",
}).format(new Date());

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatNumber(value, digits = 3) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "0";
  return Number.isInteger(number) ? String(number) : number.toFixed(digits);
}

function formatMetadata(value) {
  if (Array.isArray(value)) return value.join(" × ");
  if (value && typeof value === "object") return JSON.stringify(value);
  if (typeof value === "number") return formatNumber(value);
  return String(value ?? "");
}

function setStatus(label, className = "") {
  statusBadge.textContent = label;
  statusBadge.className = `status-badge ${className}`;
}

function reveal(stage) {
  document.querySelectorAll(`[data-reveal="${stage}"]`).forEach((section) => {
    section.classList.remove("pending-section");
    section.classList.add("revealed-section");
  });
}

function completeStage(stage, payload = {}) {
  const item = stageRail.querySelector(`[data-stage="${stage}"]`);
  if (item) item.classList.add("complete");
  reveal(stage);
  const messages = {
    source_collection: `${payload.source_count ?? 0} source captures collected.`,
    source_analysis: `${payload.feature_count ?? 0} source feature sets extracted.`,
    health_gate: `Health gate finished with ${payload.healthy_sources ?? 0} accepted sources.`,
    fusion: "Accepted source hashes fused into one digest.",
    conditioning: "Final SHA-512 conditioning complete.",
    seed_generation: "The reusable 512-bit master seed is ready.",
    experiment_save: "Source evidence and the master seed were saved permanently.",
  };
  reportNotice.textContent = messages[stage] || `${stage} complete.`;
}

function svgLineChart(values, label, unit = "") {
  if (!values?.length) return `<div class="figure-empty">No series available</div>`;
  const width = 640;
  const height = 220;
  const pad = 26;
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const points = values.map((value, index) => {
    const x = pad + (index / Math.max(1, values.length - 1)) * (width - pad * 2);
    const y = height - pad - ((value - min) / range) * (height - pad * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return `
    <svg class="data-figure" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)}">
      <path class="chart-grid" d="M${pad} ${pad}V${height - pad}H${width - pad}" />
      <polyline class="chart-line" points="${points}" />
      <text x="${pad}" y="16">${escapeHtml(label)}</text>
      <text x="${pad}" y="${height - 5}">MIN ${escapeHtml(formatNumber(min))}${escapeHtml(unit)}</text>
      <text x="${width - pad}" y="${height - 5}" text-anchor="end">MAX ${escapeHtml(formatNumber(max))}${escapeHtml(unit)}</text>
    </svg>`;
}

function svgMultiLineChart(lanes, label) {
  if (!lanes?.length) return `<div class="figure-empty">No thread lanes available</div>`;
  const colors = ["#111111", "#cc0000", "#525252", "#737373"];
  return `<div class="lane-stack"><strong>${escapeHtml(label)}</strong>${lanes.map((lane, index) => `
    <div class="lane-row"><span>T${index + 1}</span>${svgLineChart(lane, `Thread ${index + 1}`)}</div>
  `).join("")}</div>`;
}

function svgHistogram(items, label) {
  if (!items?.length) return `<div class="figure-empty">No histogram available</div>`;
  const width = 640;
  const height = 230;
  const pad = 28;
  const max = Math.max(...items.map((item) => item.count), 1);
  const barWidth = (width - pad * 2) / items.length;
  const bars = items.map((item, index) => {
    const barHeight = (item.count / max) * (height - 70);
    const x = pad + index * barWidth;
    const y = height - 38 - barHeight;
    return `<rect x="${x}" y="${y}" width="${Math.max(1, barWidth - 2)}" height="${barHeight}" />
      ${index % 3 === 0 ? `<text x="${x + barWidth / 2}" y="${height - 18}" text-anchor="middle">${escapeHtml(item.label.split("-")[0])}</text>` : ""}`;
  }).join("");
  return `<svg class="data-figure histogram" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)}">
    <text x="${pad}" y="18">${escapeHtml(label)}</text>${bars}
  </svg>`;
}

function svgScatter(pairs, label) {
  if (!pairs?.length) return `<div class="figure-empty">No lag pairs available</div>`;
  const width = 640;
  const height = 230;
  const pad = 28;
  const dots = pairs.map((pair) => {
    const x = pad + (pair.x / 255) * (width - pad * 2);
    const y = height - pad - (pair.y / 255) * (height - pad * 2);
    return `<circle cx="${x}" cy="${y}" r="3" />`;
  }).join("");
  return `<svg class="data-figure scatter" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)}">
    <path class="chart-grid" d="M${pad} ${pad}V${height - pad}H${width - pad}" />
    <text x="${pad}" y="18">${escapeHtml(label)}</text>${dots}
  </svg>`;
}

function figure(content, caption) {
  return `<figure>${content}<figcaption>${escapeHtml(caption)}</figcaption></figure>`;
}

function metadataTable(metadata = {}) {
  return `<dl class="metadata-table">${Object.entries(metadata).map(([key, value]) => `
    <div><dt>${escapeHtml(key.replaceAll("_", " "))}</dt><dd>${escapeHtml(formatMetadata(value))}</dd></div>
  `).join("")}</dl>`;
}

function cameraEvidence(source) {
  const images = source.evidence.images || {};
  return `<div class="camera-sequence">
    ${figure(`<img class="original-frame" src="${escapeHtml(images.original)}" alt="Original color camera frame used by this run" />`, "Fig. 1.1a — Exact color frame captured by the laptop camera.")}
    ${figure(`<img class="grayscale" src="${escapeHtml(images.grayscale)}" alt="Grayscale conversion of the captured camera frame" />`, "Fig. 1.1b — Color channels averaged into one grayscale value per pixel.")}
    ${figure(`<img class="pixelated" src="${escapeHtml(images.lowBits)}" alt="Low-bit noise map extracted from the camera frame" />`, "Fig. 1.1c — Two least-significant bits expanded into a visible noise map.")}
  </div>`;
}

function microphoneEvidence(source) {
  return `<div class="audio-desk">
    <div class="audio-controls">
      <button type="button" data-audio-action="play" data-audio-url="${escapeHtml(source.evidence.audio)}">Play recording</button>
      <button type="button" data-audio-action="stop">Stop</button>
      <label>Speed
        <select id="audioSpeed">
          <option value="0.01">0.01x</option><option value="0.1">0.10x</option><option value="0.25">0.25x</option>
          <option value="0.5">0.50x</option><option value="1" selected>1.00x</option><option value="2">2.00x</option>
        </select>
      </label>
    </div>
    <p class="technical-copy">The saved one-second WAV is the exact PCM block used before adjacent sample differences are reduced to low bits.</p>
    <div class="figure-pair">
      ${figure(svgLineChart(source.evidence.originalSeries, "Original PCM waveform", ""), "Fig. 1.2a — Downsampled view of the saved microphone PCM samples.")}
      ${figure(svgLineChart(source.evidence.deltaSeries, "Adjacent-sample deltas", ""), "Fig. 1.2b — Differences reveal rapid changes before low-bit extraction.")}
    </div>
  </div>`;
}

function timingEvidence(source) {
  const isScheduler = source.evidence.kind === "scheduler_jitter";
  return `<div class="figure-pair">
    ${isScheduler ? figure(svgMultiLineChart(source.evidence.threadLanes, "Per-thread yield timing"), "Fig. 1.4a — Each lane shows timing variation after scheduler yields.") : figure(svgLineChart(source.evidence.timingSeries, "Measured CPU timing deltas", "ns"), "Fig. 1.3a — Nanosecond deltas between repeated CPU operations.")}
    ${figure(svgLineChart(source.evidence.lowByteSeries, "Low byte retained for entropy", ""), `${isScheduler ? "Fig. 1.4b" : "Fig. 1.3b"} — Each timing delta is reduced to its lowest eight bits.`)}
  </div>`;
}

function missingEvidence(source) {
  return `<div class="missing-evidence">
    <p class="section-label">Evidence unavailable</p>
    <h4>${escapeHtml(source.label)} collection did not produce a saved capture.</h4>
    <p>${escapeHtml(source.reasons.length ? source.reasons.join("; ") : "No source evidence was returned.")}</p>
  </div>`;
}

function renderSources(sources) {
  sourceGrid.innerHTML = sources.map((source, index) => {
    const evidence = source.evidence.kind === "camera"
      ? cameraEvidence(source)
      : source.evidence.kind === "microphone"
        ? microphoneEvidence(source)
        : ["cpu_jitter", "scheduler_jitter"].includes(source.evidence.kind)
          ? timingEvidence(source)
          : missingEvidence(source);
    return `<article class="source-report">
      <header class="article-header">
        <div><p class="section-label">Source ${index + 1} / ${escapeHtml(source.health)}</p><h3>${escapeHtml(source.label)}</h3></div>
        <strong class="health-word ${escapeHtml(source.health)}">${escapeHtml(source.health)}</strong>
      </header>
      ${evidence}
      <div class="transformation-strip">
        <span>Human-readable capture</span><b>→</b><span>Measured values</span><b>→</b><span>Low bits packed</span><b>→</b><span>${escapeHtml(source.byteCount)} saved bytes</span>
      </div>
      <div class="source-data-grid">
        ${figure(svgLineChart(source.visual.series, "Extracted entropy byte stream", ""), "The byte stream that enters feature extraction and source hashing.")}
        ${figure(svgHistogram(source.visual.histogram, "Byte-frequency groups"), "Counts grouped into sixteen hexadecimal ranges.")}
      </div>
      <div class="source-footer-grid">
        <div><h4>Capture metadata</h4>${metadataTable(source.visual.metadata)}</div>
        <div><h4>First 32 bytes</h4><code class="hex-block">${escapeHtml(source.visual.hexPreview)}</code><p class="file-reference">${escapeHtml(source.inputFile)}</p></div>
      </div>
    </article>`;
  }).join("");
}

function thresholdRow(label, value, max, note, pass) {
  const percent = Math.max(0, Math.min(100, (Number(value) / max) * 100));
  return `<div class="threshold-row">
    <div><strong>${escapeHtml(label)}</strong><span>${escapeHtml(formatNumber(value))} / ${escapeHtml(note)}</span></div>
    <div class="threshold-track"><i style="width:${percent}%"></i></div>
    <b class="${pass ? "pass-text" : "fail-text"}">${pass ? "PASS" : "FAIL"}</b>
  </div>`;
}

function renderHealth(sources, thresholds) {
  healthGrid.innerHTML = sources.map((source, index) => {
    const checks = Object.fromEntries(source.checks.map((check) => [check.name, check.passed]));
    return `<article class="health-report">
      <header class="article-header">
        <div><p class="section-label">Fig. 2.${index + 1}</p><h3>${escapeHtml(source.label)}</h3></div>
        <strong class="health-word ${escapeHtml(source.health)}">${escapeHtml(source.health)} ${escapeHtml(source.score)}</strong>
      </header>
      <div class="health-layout">
        <div>
          ${thresholdRow("Unique bytes", source.uniqueBytes, 256, `minimum ${thresholds.minimumUniqueBytes}`, checks["minimum unique bytes"])}
          ${thresholdRow("Bit balance", source.bitBalance, 1, `${thresholds.minimumBitBalance}–${thresholds.maximumBitBalance}`, checks["bit balance range"])}
          ${thresholdRow("Shannon entropy", source.entropy, 8, `minimum ${thresholds.minimumEntropy}`, checks["entropy minimum"])}
          ${thresholdRow("Health score", source.score, 1, "1.0", source.health === "pass")}
          <div class="reason-box"><strong>Gate explanation</strong><p>${escapeHtml(source.reasons.length ? source.reasons.join("; ") : "All broad health checks passed.")}</p></div>
        </div>
        <div>
          ${figure(svgHistogram(source.visual.histogram, "Byte-frequency distribution"), "A source dominated by a few byte groups is easier to detect here.")}
          ${figure(svgScatter(source.visual.lagPairs, "Lag-1 byte pairs"), `Autocorrelation estimate: ${source.autocorrelation}. A tight pattern can indicate dependence.`)}
        </div>
      </div>
    </article>`;
  }).join("");
}

function digestBlock(label, digest, caption) {
  return `<article class="digest-block"><p class="section-label">${escapeHtml(label)}</p><code>${escapeHtml(digest)}</code><p>${escapeHtml(caption)}</p></article>`;
}

function hexToBytes(hex) {
  return String(hex ?? "").match(/.{1,2}/g)?.map((pair) => Number.parseInt(pair, 16)) || [];
}

function byteCells(values, label, className = "byte-strip") {
  const bytes = values || [];
  if (!bytes.length) return `<div class="figure-empty">No bytes available</div>`;
  return `<div class="${className}" role="img" aria-label="${escapeHtml(label)}">
    ${bytes.map((value, index) => {
      const byte = Number(value) || 0;
      const alpha = (0.16 + (byte / 255) * 0.84).toFixed(3);
      const textColor = byte > 145 ? "#f9f9f7" : "#111111";
      return `<span style="background-color:rgba(204,0,0,${alpha});color:${textColor}" title="Byte ${index + 1}: ${byte}">${byte.toString(16).padStart(2, "0")}</span>`;
    }).join("")}
  </div>`;
}

function sourceHashFigure(item, index) {
  const digestBytes = hexToBytes(item.digest).slice(0, 16);
  const sourceLabel = item.source.replaceAll("_", " ");
  return `<figure class="source-hash-figure">
    <div class="source-hash-heading"><strong>3.1.${index + 1} ${escapeHtml(sourceLabel)}</strong><span>First 16 bytes shown</span></div>
    <div class="source-hash-flow">
      <div><b>Accepted source bytes</b>${byteCells(item.rawPreview, `${sourceLabel} accepted source byte preview`)}</div>
      <span class="hash-arrow" aria-hidden="true">&rarr;</span>
      <div><b>SHA-512 digest bytes</b>${byteCells(digestBytes, `${sourceLabel} SHA-512 digest byte preview`)}</div>
    </div>
    <figcaption>Byte intensity encodes value from 00 to ff. The full digest remains printed below.</figcaption>
  </figure>`;
}

function fusionDiagram(sourceHashes) {
  const height = Math.max(240, sourceHashes.length * 58 + 58);
  const centerY = height / 2;
  const branches = sourceHashes.map((item, index) => {
    const y = 48 + index * 58;
    const label = escapeHtml(item.source.replaceAll("_", " "));
    return `<text x="24" y="${y - 9}">${label}</text>
      <line x1="24" y1="${y}" x2="330" y2="${y}" />
      <line x1="330" y1="${y}" x2="440" y2="${centerY}" />
      <circle cx="24" cy="${y}" r="5" />`;
  }).join("");
  return `<svg class="fusion-diagram" viewBox="0 0 900 ${height}" role="img" aria-label="${sourceHashes.length} accepted source hashes converge in stable source-name order into one HG-MSEF fused digest">
    ${branches}
    <rect x="440" y="${centerY - 42}" width="190" height="84" />
    <text class="fusion-node-title" x="535" y="${centerY - 6}" text-anchor="middle">HG-MSEF</text>
    <text x="535" y="${centerY + 18}" text-anchor="middle">stable ordered fusion</text>
    <line x1="630" y1="${centerY}" x2="850" y2="${centerY}" />
    <path class="fusion-arrowhead" d="M850 ${centerY}l-18 -10v20z" />
    <text x="850" y="${centerY - 16}" text-anchor="end">one fused digest</text>
  </svg>`;
}

function digestHeatmap(label, digest) {
  return `<figure class="digest-heatmap-figure">
    <div class="source-hash-heading"><strong>${escapeHtml(label)}</strong><span>64 bytes / 8 × 8</span></div>
    ${byteCells(hexToBytes(digest), `${label}, byte intensity heatmap`, "byte-heatmap")}
    <figcaption>Darker red cells represent larger byte values.</figcaption>
  </figure>`;
}

function rejectionDiagram(rejection) {
  const maximum = 2 ** 32;
  const candidate = Number(rejection.candidate);
  const limit = Number(rejection.limit);
  const pad = 58;
  const width = 784;
  const candidateX = pad + (candidate / maximum) * width;
  const limitX = pad + (limit / maximum) * width;
  const anchor = candidateX > 650 ? "end" : "start";
  const labelX = candidateX > 650 ? candidateX - 8 : candidateX + 8;
  return `<svg class="rejection-diagram" viewBox="0 0 900 230" role="img" aria-label="The candidate ${escapeHtml(candidate)} is below the acceptance limit ${escapeHtml(limit)} and is accepted">
    <text x="${pad}" y="26">32-bit candidate space</text>
    <line class="accepted-range" x1="${pad}" y1="100" x2="${limitX}" y2="100" />
    <line class="rejected-range" x1="${limitX}" y1="100" x2="${pad + width}" y2="100" />
    <line class="axis-tick" x1="${pad}" y1="88" x2="${pad}" y2="114" />
    <line class="limit-tick" x1="${limitX}" y1="72" x2="${limitX}" y2="126" />
    <line class="axis-tick" x1="${pad + width}" y1="88" x2="${pad + width}" y2="114" />
    <circle class="candidate-marker" cx="${candidateX}" cy="100" r="9" />
    <line class="candidate-guide" x1="${candidateX}" y1="100" x2="${candidateX}" y2="52" />
    <text class="candidate-label" x="${labelX}" y="46" text-anchor="${anchor}">candidate ${escapeHtml(candidate)}</text>
    <text x="${pad}" y="140">0</text>
    <text class="limit-label" x="${limitX - 8}" y="164" text-anchor="end">limit ${escapeHtml(limit)}</text>
    <text x="${pad + width}" y="140" text-anchor="end">2^32</text>
    <text x="${pad}" y="184">Accepted range</text>
    <rect class="tail-inset" x="580" y="166" width="262" height="28" />
    <text class="tail-label" x="711" y="214" text-anchor="middle">Rejected tail magnified: ${escapeHtml(maximum - limit)} values</text>
  </svg>`;
}

function renderTransformation(data) {
  if (!data?.sourceHashes?.length || !data.seedHex) {
    transformationReport.innerHTML = `<div class="missing-evidence"><p class="section-label">Transformation unavailable</p><h4>The health gate did not admit enough sources to generate a seed.</h4></div>`;
    return;
  }
  const sourceHashes = data.sourceHashes || [];
  transformationReport.innerHTML = `
    <article class="transformation-figure-block">
      <p class="section-label">Fig. 3.1 — Source bytes become source hashes</p>
      <div class="source-hash-figures">${sourceHashes.map(sourceHashFigure).join("")}</div>
    </article>
    <div class="hash-columns">${sourceHashes.map((item, index) => digestBlock(
      `Full hash 3.1.${index + 1} ${item.source.replaceAll("_", " ")}`,
      item.digest,
      "SHA-512 binds source identity, run ID, raw bytes, and metadata digest.",
    )).join("")}</div>
    <article class="transformation-figure-block">
      <p class="section-label">Fig. 3.2 — Accepted hashes converge into fusion</p>
      ${fusionDiagram(sourceHashes)}
      <p class="diagram-note">Lines show stable source-name order and convergence. They do not encode hash similarity or magnitude.</p>
    </article>
    <article class="transformation-figure-block">
      <p class="section-label">Fig. 3.3 — Fusion, conditioning, and master seed</p>
      <div class="digest-heatmap-pair">
        ${digestHeatmap("Fused digest", data.fusedDigest)}
        ${digestHeatmap("Conditioned digest", data.conditionedDigest)}
      </div>
    </article>
    <div class="digest-pair">
      ${digestBlock("Exact fused digest", data.fusedDigest, "One digest represents all accepted sources and the run context.")}
      ${digestBlock("Exact master seed", data.seedHex, "The conditioned 512-bit digest becomes the reusable master seed.")}
    </div>
    <article class="seed-ready-report">
      <p class="section-label">Seed ready</p>
      <code>${escapeHtml(data.seedHex)}</code>
      <p>Output generators derive isolated child seeds from this value. Choosing one output does not change another.</p>
    </article>`;
}

function renderSavedRun(data) {
  seedValue.textContent = data.seed || "Seed unavailable";
  savePanel.innerHTML = `
    <dl class="save-table">
      <div><dt>Run ID</dt><dd>${escapeHtml(data.runId)}</dd></div>
      <div><dt>Status</dt><dd>${escapeHtml(data.status)}</dd></div>
      <div><dt>Experiment</dt><dd>${escapeHtml(data.experimentId)}</dd></div>
      <div><dt>Output index</dt><dd>${escapeHtml(data.outputIndex)}</dd></div>
      <div><dt>Experiment path</dt><dd>${escapeHtml(data.experimentPath)}</dd></div>
    </dl>`;
}

function renderResult(data) {
  currentRun = data;
  outputChoices.querySelectorAll("button").forEach((item) => item.disabled = !data.seed);
  renderSources(data.sources);
  renderHealth(data.sources, data.thresholds);
  renderTransformation(data.transformation);
  renderSavedRun(data);
  setStatus(data.status, data.status);
  ["source_collection", "source_analysis", "health_gate", "fusion", "conditioning", "seed_generation", "experiment_save"].forEach(reveal);
  const parameters = new URLSearchParams(window.location.search);
  const focus = parameters.get("focus");
  if (focus) document.body.classList.add(`focus-${focus}`);
  const requestedOutput = parameters.get("output");
  const outputButton = outputChoices.querySelector(`[data-output-kind="${requestedOutput}"]`);
  if (outputButton) window.setTimeout(() => outputButton.click(), 100);
}

function resetReport() {
  stageRail.querySelectorAll("li").forEach((item) => item.classList.remove("complete"));
  document.querySelectorAll("[data-reveal]").forEach((section) => {
    section.classList.add("pending-section");
    section.classList.remove("revealed-section");
  });
  sourceGrid.innerHTML = `<p class="empty-copy">Collecting source evidence…</p>`;
  healthGrid.innerHTML = `<p class="empty-copy">Waiting for feature extraction and health checks…</p>`;
  transformationReport.innerHTML = `<p class="empty-copy">Waiting for accepted source hashes…</p>`;
  currentRun = null;
  outputChoices.querySelectorAll("button").forEach((item) => item.disabled = true);
  seedValue.textContent = "Waiting for seed creation";
  outputResult.innerHTML = "<p>Select an output after the seed is ready.</p>";
  savePanel.innerHTML = "<p>Experiment paths appear after the report is saved.</p>";
}

function renderOtpOutput(payload, artifact) {
  return `<article class="selected-output otp-output">
    <div><p class="section-label">Selected output / OTP</p><h3>${escapeHtml(payload.otp)}</h3>
      <p>The OTP is generated only after selection. Rejection sampling avoids simple modulo bias.</p></div>
    <div>
      ${rejectionDiagram(payload.rejection)}
      <div class="rejection-equation">
        <span>Candidate <strong>${escapeHtml(payload.rejection.candidate)}</strong></span>
        <span>&lt; acceptance limit <strong>${escapeHtml(payload.rejection.limit)}</strong></span>
        <span>accepted after <strong>${escapeHtml(payload.rejection.inspected)}</strong> inspected chunk(s)</span>
        <span>uniform value <strong>${escapeHtml(payload.rejection.value)}</strong></span>
      </div>
    </div>
    <a class="artifact-link" href="${escapeHtml(artifact)}">Open saved OTP JSON</a>
  </article>`;
}

function renderMapOutput(payload, artifact) {
  const legend = payload.palette.map((item) => `<span><i style="background:${escapeHtml(item.color)}"></i>${escapeHtml(item.label)}</span>`).join("");
  return `<article class="selected-output">
    <div><p class="section-label">Selected output / Map</p><h3>Five-color terrain map</h3>
      <p>A deterministic ${payload.width} by ${payload.height} terrain field derived from the saved seed.</p></div>
    <canvas id="terrainMapCanvas" class="terrain-map" width="${payload.width}" height="${payload.height}" role="img" aria-label="Generated ${payload.width} by ${payload.height} terrain map"></canvas>
    <div class="terrain-legend">${legend}</div>
    <a class="artifact-link" href="${escapeHtml(artifact)}">Open saved map JSON</a>
  </article>`;
}

function drawTerrainMap(payload) {
  const canvas = document.querySelector("#terrainMapCanvas");
  const context = canvas?.getContext("2d");
  if (!context) return;

  const colors = Object.fromEntries(payload.palette.map((item) => {
    const value = item.color.slice(1);
    return [item.index, [
      Number.parseInt(value.slice(0, 2), 16),
      Number.parseInt(value.slice(2, 4), 16),
      Number.parseInt(value.slice(4, 6), 16),
    ]];
  }));
  const image = context.createImageData(payload.width, payload.height);
  let offset = 0;
  payload.cells.forEach((row) => row.forEach((cell) => {
    const [red, green, blue] = colors[cell];
    image.data[offset] = red;
    image.data[offset + 1] = green;
    image.data[offset + 2] = blue;
    image.data[offset + 3] = 255;
    offset += 4;
  }));
  context.putImageData(image, 0, 0);
}

function mazeSvg(payload) {
  const cellSize = 20;
  const width = payload.width * cellSize;
  const height = payload.height * cellSize;
  const { north, east, south, west } = payload.wallBits;
  const paths = [];
  payload.cells.forEach((row, rowIndex) => row.forEach((walls, columnIndex) => {
    const x = columnIndex * cellSize;
    const y = rowIndex * cellSize;
    if (walls & north) paths.push(`M${x} ${y}H${x + cellSize}`);
    if (walls & west) paths.push(`M${x} ${y}V${y + cellSize}`);
    if (columnIndex === payload.width - 1 && walls & east) paths.push(`M${x + cellSize} ${y}V${y + cellSize}`);
    if (rowIndex === payload.height - 1 && walls & south) paths.push(`M${x} ${y + cellSize}H${x + cellSize}`);
  }));
  return `<svg class="maze-map" viewBox="0 0 ${width} ${height}" role="img" aria-label="Generated 30 by 30 maze with closed outer boundary">
    <rect class="maze-start" x="3" y="3" width="${cellSize - 6}" height="${cellSize - 6}" />
    <rect class="maze-end" x="${width - cellSize + 3}" y="${height - cellSize + 3}" width="${cellSize - 6}" height="${cellSize - 6}" />
    <path d="${paths.join("")}" />
  </svg>`;
}

function renderMazeOutput(payload, artifact) {
  return `<article class="selected-output">
    <div><p class="section-label">Selected output / Maze</p><h3>Fixed 30 × 30 perfect maze</h3>
      <p>The outside boundary remains closed. Red marks the start cell and green marks the end cell.</p></div>
    ${mazeSvg(payload)}
    <a class="artifact-link" href="${escapeHtml(artifact)}">Open saved maze JSON</a>
  </article>`;
}

async function requestOutput(kind, button) {
  if (!currentRun?.seed) return;
  outputChoices.querySelectorAll("button").forEach((item) => item.disabled = true);
  button.textContent = `Generating ${kind}`;
  outputResult.innerHTML = `<p class="empty-copy">Deriving the ${escapeHtml(kind)} child seed and generating output…</p>`;
  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        kind,
        seed: currentRun.seed,
        experimentId: currentRun.experimentId,
        runId: currentRun.runId,
      }),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(result.error || "generation failed");
    outputResult.innerHTML = kind === "otp"
      ? renderOtpOutput(result.output, result.artifact)
      : kind === "map"
        ? renderMapOutput(result.output, result.artifact)
        : renderMazeOutput(result.output, result.artifact);
    if (kind === "map") drawTerrainMap(result.output);
  } catch (error) {
    outputResult.innerHTML = `<div class="missing-evidence"><p class="section-label">Output generation failed</p><p>${escapeHtml(error.message)}</p></div>`;
  } finally {
    outputChoices.querySelectorAll("button").forEach((item) => item.disabled = false);
    button.textContent = `Generate ${kind.toUpperCase()}`;
  }
}

function runFlow() {
  if (eventSource) eventSource.close();
  resetReport();
  startButton.disabled = true;
  startButton.textContent = "Live run in progress";
  setStatus("Running", "running");
  reportNotice.textContent = "Requesting camera, microphone, CPU jitter, and scheduler jitter.";
  eventSource = new EventSource("/api/run-stream");
  eventSource.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "stage") completeStage(message.stage, message.payload);
    if (message.type === "result") {
      renderResult(message.payload);
      eventSource.close();
      startButton.disabled = false;
      startButton.textContent = "Start another live run";
    }
    if (message.type === "error") {
      reportNotice.textContent = message.error;
      setStatus("Failed", "failed");
      eventSource.close();
      startButton.disabled = false;
      startButton.textContent = "Retry live source run";
    }
  };
  eventSource.onerror = () => {
    if (startButton.disabled) {
      reportNotice.textContent = "The live stream closed before the report completed.";
      setStatus("Failed", "failed");
      startButton.disabled = false;
      startButton.textContent = "Retry live source run";
    }
    eventSource.close();
  };
}

async function playAudio(url, rate) {
  audioContext ||= new AudioContext();
  if (!audioBuffers.has(url)) {
    const response = await fetch(url);
    audioBuffers.set(url, await audioContext.decodeAudioData(await response.arrayBuffer()));
  }
  if (activeAudioSource) activeAudioSource.stop();
  activeAudioSource = audioContext.createBufferSource();
  activeAudioSource.buffer = audioBuffers.get(url);
  activeAudioSource.playbackRate.value = rate;
  activeAudioSource.connect(audioContext.destination);
  activeAudioSource.start();
}

document.addEventListener("click", (event) => {
  const outputControl = event.target.closest("[data-output-kind]");
  if (outputControl) {
    requestOutput(outputControl.dataset.outputKind, outputControl);
    return;
  }
  const control = event.target.closest("[data-audio-action]");
  if (!control) return;
  if (control.dataset.audioAction === "stop" && activeAudioSource) {
    activeAudioSource.stop();
    activeAudioSource = null;
  }
  if (control.dataset.audioAction === "play") {
    const speed = Number(document.querySelector("#audioSpeed")?.value || 1);
    playAudio(control.dataset.audioUrl, speed).catch((error) => {
      reportNotice.textContent = `Audio playback failed: ${error.message}`;
    });
  }
});

startButton.addEventListener("click", runFlow);

if (new URLSearchParams(window.location.search).get("autorun") === "1") {
  window.setTimeout(runFlow, 400);
}

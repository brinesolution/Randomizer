const startButton = document.querySelector("#startButton");
const statusBadge = document.querySelector("#statusBadge");
const requestGrid = document.querySelector("#requestGrid");
const sourceGrid = document.querySelector("#sourceGrid");
const traceList = document.querySelector("#traceList");
const otpValue = document.querySelector("#otpValue");
const savePanel = document.querySelector("#savePanel");

const requestedSources = ["camera", "microphone", "cpu_jitter", "scheduler_jitter"];

function setStatus(label, state) {
  statusBadge.textContent = label;
  statusBadge.className = `status-badge ${state}`;
}

function setRequestState(state) {
  requestedSources.forEach((name) => {
    const card = requestGrid.querySelector(`[data-source="${name}"]`);
    if (!card) {
      return;
    }
    card.className = `request-card ${state}`;
    const label = state === "active" ? "Requested" : state === "done" ? "Collected" : "Waiting";
    card.querySelector("strong").textContent = label;
  });
}

function formatNumber(value, digits = 4) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "0";
  }
  return Number.isInteger(value) ? String(value) : value.toFixed(digits);
}

function metric(label, value) {
  return `<div class="metric-row"><span>${label}</span><strong>${value}</strong></div>`;
}

function renderSources(sources) {
  sourceGrid.className = "source-grid";
  sourceGrid.innerHTML = sources
    .map((source) => {
      const checks = source.checks
        .map((check) => `<li class="${check.passed ? "pass" : "fail"}">${check.name}</li>`)
        .join("");
      const reasons = source.reasons.map((reason) => `<li>${reason}</li>`).join("");
      return `
        <article class="source-card ${source.health}">
          <div class="card-topline">
            <span>${source.label}</span>
            <strong>${source.health}</strong>
          </div>
          <div class="source-number" aria-hidden="true">${source.score}</div>
          <div class="metric-grid">
            ${metric("Bytes", formatNumber(source.byteCount, 0))}
            ${metric("Unique", formatNumber(source.uniqueBytes, 0))}
            ${metric("Bit balance", formatNumber(source.bitBalance))}
            ${metric("Entropy", formatNumber(source.entropy))}
            ${metric("Autocorr", formatNumber(source.autocorrelation))}
            ${metric("Hash head", source.hashPreview || "missing")}
          </div>
          <div class="check-columns">
            <div>
              <h3>Checks</h3>
              <ul>${checks}</ul>
            </div>
            <div>
              <h3>Reasons</h3>
              <ul>${reasons}</ul>
            </div>
          </div>
          <p class="path-line">${source.inputFile || "input not saved"}</p>
        </article>
      `;
    })
    .join("");
}

function renderTrace(steps) {
  traceList.className = "trace-list";
  traceList.innerHTML = steps
    .map((step) => {
      const metrics = Object.entries(step.metrics || {})
        .map(([key, value]) => metric(key.replaceAll("_", " "), typeof value === "object" ? JSON.stringify(value) : value))
        .join("");
      return `
        <article class="trace-step ${step.status}">
          <span class="step-order">${String(step.order).padStart(2, "0")}</span>
          <div>
            <div class="card-topline">
              <h3>${step.title}</h3>
              <strong>${step.status}</strong>
            </div>
            <p>${step.summary}</p>
            <div class="metric-grid compact">${metrics}</div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderSavedRun(data) {
  otpValue.textContent = data.otp || "------";
  savePanel.innerHTML = `
    <div class="metric-grid compact">
      ${metric("Run id", data.runId)}
      ${metric("Status", data.status)}
      ${metric("Experiment", data.experimentId)}
    </div>
    <p class="path-line">${data.experimentPath}</p>
    <p class="path-line">${data.outputIndex}</p>
  `;
}

function renderError(message) {
  sourceGrid.className = "source-grid empty-state error-state";
  sourceGrid.innerHTML = `<p>${message}</p>`;
  traceList.className = "trace-list empty-state error-state";
  traceList.innerHTML = "<p>The run did not complete.</p>";
  otpValue.textContent = "FAILED";
}

async function runFlow() {
  startButton.disabled = true;
  startButton.textContent = "Collecting Sources";
  setStatus("Running", "running");
  setRequestState("active");
  otpValue.textContent = "......";
  savePanel.innerHTML = "<p>Experiment save pending.</p>";

  try {
    const response = await fetch("/api/run", { method: "POST" });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      throw new Error(data.error || "Run failed");
    }
    renderSources(data.sources);
    renderTrace(data.trace);
    renderSavedRun(data);
    setStatus(data.status, data.status);
    setRequestState("done");
  } catch (error) {
    renderError(error.message);
    setStatus("Failed", "failed");
  } finally {
    startButton.disabled = false;
    startButton.textContent = "Start Source Run";
  }
}

startButton.addEventListener("click", runFlow);

if (new URLSearchParams(window.location.search).get("autorun") === "1") {
  window.setTimeout(runFlow, 500);
}

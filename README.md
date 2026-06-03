# Randomiser

Randomiser is a Python project for collecting entropy-like signals from a laptop, conditioning them through a shared pipeline, and generating 6-digit OTPs in two modes: continuous batch mode and a visual web mode.

This is a research and portfolio prototype. It is not a certified cryptographic TRNG and it must not be used for production authentication or security-critical OTP flows.

**Install**

```bash
python -m pip install -e .
```

**Run modes**

`Batch mode`

- Runs from VS Code or a terminal.
- Saves source input files and OTP output rows into one experiment folder.

Planned commands:

```bash
python scripts/run_once.py
python scripts/generate_dataset.py --config config/batch_run.yaml
```

`Web mode`

- Shows the pipeline step by step: source collection, transformation, health gating, fusion, conditioning, and OTP output.
- Uses the same backend and experiment storage contract as batch mode.

Planned command:

```bash
streamlit run apps/web/app.py
```

**Experiment storage**

```text
data/experiments/<experiment_id>/
  manifest.json
  input/
    camera/
    microphone/
    cpu_jitter/
    scheduler_jitter/
  output/
    run_index.csv
  logs/
```

Each OTP run uses one shared `run_id` filename stem across the four source input files, and the output CSV stores those filenames with the generated OTP in the same row.

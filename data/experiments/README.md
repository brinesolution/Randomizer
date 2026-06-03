Experiments are stored as:

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

Every run uses one shared run ID as the filename stem for all source input files.

Example:

```text
run_000001
```

That run maps to:

```text
input/camera/run_000001.bin
input/microphone/run_000001.bin
input/cpu_jitter/run_000001.bin
input/scheduler_jitter/run_000001.bin
```

The result is recorded in `output/run_index.csv`.

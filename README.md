# Randomiser

Multi-source entropy OTP generator.

This scaffold is now trimmed to an MVP-first structure.

Current scope:
- entropy source collection
- health-gated fusion pipeline
- OTP generation
- basic run logging
- CLI and dataset generation scripts
- lightweight web app for visualizing the generation process

Run modes:
- Web mode: shows source collection, source transformation, health gating, fusion, and the produced OTP.
- Batch mode: runs continuously from VS Code or a terminal and writes every run to an experiment folder.

Experiment storage:
- `data/experiments/<experiment_id>/input/camera/`
- `data/experiments/<experiment_id>/input/microphone/`
- `data/experiments/<experiment_id>/input/cpu_jitter/`
- `data/experiments/<experiment_id>/input/scheduler_jitter/`
- `data/experiments/<experiment_id>/output/run_index.csv`

For each run, all source input files share the same `run_id` filename stem. The output CSV stores those input filenames and the resulting OTP in the same row.

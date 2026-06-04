# Dataset Schema

Each experiment stores source inputs, seed rows, and optional generated
outputs.

```text
data/experiments/<experiment_id>/
  manifest.json
  input/<source_name>/<run_id>.bin
  output/
    run_index.csv
    generated/
      otp/<run_id>.json
      map/<run_id>.json
      maze/<run_id>.json
  logs/
```

All files from one run use the same `run_id`.

`output/run_index.csv` columns:

```csv
run_id,mode,camera_input_file,microphone_input_file,cpu_jitter_input_file,scheduler_jitter_input_file,seed_hex,status,created_at
```

`seed_hex` contains the 64-byte master seed as 128 hexadecimal characters.
Missing source columns remain empty in degraded or source-specific runs.

Generated output JSON files contain their output kind, deterministic data, and
a hash of the domain-separated child seed.

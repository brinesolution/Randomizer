Experiment folders use one directory per experiment:

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

Each OTP run uses one shared `run_id` filename stem across all source input files.

Example:

```text
input/camera/run_000001.bin
input/microphone/run_000001.bin
input/cpu_jitter/run_000001.bin
input/scheduler_jitter/run_000001.bin
```

The output CSV keeps the source filenames and OTP result together:

```csv
run_id,mode,camera_input_file,microphone_input_file,cpu_jitter_input_file,scheduler_jitter_input_file,otp,status,created_at
run_000001,batch,input/camera/run_000001.bin,input/microphone/run_000001.bin,input/cpu_jitter/run_000001.bin,input/scheduler_jitter/run_000001.bin,493820,ok,2026-06-04T00:00:00Z
```

Both web mode and batch mode write through the same experiment storage contract.

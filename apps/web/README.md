# Randomiser Web App

Local Node web mode for showing one OTP run from source request to saved output.

Run from the project root:

```powershell
npm --prefix apps/web start
```

Alternative:

```powershell
python scripts/run_web.py
```

Open `http://localhost:4173`, press `Start Source Run`, and allow laptop camera and microphone access when the OS requests it. Each run is saved under `data/experiments/<experiment_id>/` with source inputs and `output/run_index.csv`.

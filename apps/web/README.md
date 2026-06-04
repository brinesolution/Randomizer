# Randomiser Web App

Local educational web mode that runs the real Randomiser pipeline and reveals
each completed stage automatically.

Run from the project root:

```powershell
python scripts/run_web.py
```

Alternatively:

```powershell
npm --prefix apps/web start
```

Open `http://localhost:4173` and press `Start Live Source Run`. The Python
backend collects from the laptop camera, microphone, CPU jitter, and scheduler
jitter sources. Camera and microphone access may require operating-system
permission.

The report reveals source evidence, feature extraction, health checks, source
hashing, fusion, conditioning, rejection sampling, and the final OTP as the
real backend stages finish.

Each run is saved permanently under:

```text
data/experiments/<experiment_id>/
  input/<source_name>/<run_id>.bin
  output/previews/camera/<run_id>_original.jpg
  output/previews/camera/<run_id>_grayscale.png
  output/previews/camera/<run_id>_lowbit.png
  output/previews/microphone/<run_id>.wav
  output/run_index.csv
```

The microphone preview contains the one-second web capture and supports
playback speeds from `0.01x` to `2x`.

Optional QA views:

```text
http://localhost:4173/?autorun=1&focus=health
http://localhost:4173/?autorun=1&focus=transformation
http://localhost:4173/?autorun=1&focus=otp
```

Endpoints:

- `GET /api/health`: server health
- `GET /api/run-stream`: one run as server-sent stage events
- `POST /api/run`: one completed run as JSON
- `GET /artifacts/<experiment_id>/...`: saved run artifacts

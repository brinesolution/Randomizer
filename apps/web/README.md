# Randomiser web app

The local web app runs the real source pipeline, stops after reusable seed
creation, and then lets the user generate an OTP, terrain map, or maze from
that saved seed.

Run from the project root:

```powershell
python scripts/run_web.py
```

Open `http://localhost:4173` and press `Start Live Source Run`.

The report reveals source evidence, feature extraction, health checks, source
hashing, HG-MSEF fusion, conditioning, and the final 512-bit seed. Output
controls become available only after the seed is saved.

Endpoints:

- `GET /api/health`: server health
- `GET /api/run-stream`: one seed run as server-sent stage events
- `POST /api/run`: one completed seed run as JSON
- `POST /api/generate`: generate and save an OTP, map, or maze
- `GET /artifacts/<experiment_id>/...`: saved run artifacts

Optional QA views:

```text
http://localhost:4173/?autorun=1&focus=output&output=otp
http://localhost:4173/?autorun=1&focus=output&output=map
http://localhost:4173/?autorun=1&focus=output&output=maze
```

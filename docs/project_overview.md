Randomiser is a laptop-based MVP for collecting noisy source bytes, checking basic source health, and generating a six digit OTP for experiments.

The project has two intended modes:

- Batch mode runs from the terminal and can generate many OTP rows without stopping.
- Web mode will show the same backend process visually after the backend is stable.

The current backend flow is:

1. Collect source bytes from enabled sources.
2. Extract simple byte-level features.
3. Run broad health checks and decide ok, degraded, or failed.
4. Hash each accepted source independently.
5. Fuse accepted source hashes with run context.
6. Condition the fused bytes with SHA-512.
7. Use rejection sampling to format a six digit OTP.
8. Save source input files and the output CSV row under one experiment folder.

This is an experimental project and is not a certified random number generator or production OTP system.

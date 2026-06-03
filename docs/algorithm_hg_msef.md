HG-MSEF is the project name for the MVP source fusion step.

The current implementation does this:

1. Run source health checks.
2. Accept sources with `pass` status and, by default, `warn` status.
3. Hash each accepted source independently using source name, run id, raw bytes, and a metadata digest.
4. Sort source hashes by stable source name.
5. Combine source hashes with run context.
6. Hash the combined payload with SHA-512.
7. Run final conditioning before OTP conversion.

The sorting step makes fusion deterministic even when sources are collected concurrently. The metadata digest prevents source metadata from changing silently without affecting the source hash.

Failed sources are excluded from fusion. If fewer than the configured minimum number of sources are healthy, generation returns failed status and no OTP.

# HG-MSEF Seed Fusion

HG-MSEF is the project name for Randomiser's source-fusion step.

Current flow:

1. Run source health checks.
2. Accept sources with `pass` or configured `warn` status.
3. Hash each accepted source with its name, run ID, raw bytes, and metadata
   digest.
4. Sort source hashes by stable source name.
5. Combine source hashes with run context.
6. Hash the combined payload with SHA-512.
7. Apply final domain-separated SHA-512 conditioning.
8. Save the conditioned digest as the reusable master seed.

Failed sources are excluded from fusion. If fewer than the configured minimum
number remain, the run fails and no seed or generated output is produced.

# Project Overview

Randomiser is a laptop-based experimental master-seed generator.

It collects noisy source bytes, measures broad source health, hashes accepted
sources, performs stable HG-MSEF fusion, and conditions the result into one
512-bit seed.

After seed creation, users may generate:

- a six-digit OTP;
- a five-color terrain map;
- a fixed 30 by 30 maze.

Web mode explains one live seed run and provides output controls. Batch mode
creates many seeds and may optionally save one selected output for each run.

This is not a certified random number generator or production security
service.

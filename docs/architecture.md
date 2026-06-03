The codebase uses a `src/` layout and keeps each responsibility in a small package.

Core modules:

- `randomiser.core`: enums, dataclasses, config loading, paths, timing, hashing, and shared exceptions.
- `randomiser.sources`: laptop source collectors and the source registry.
- `randomiser.integrations`: low-level camera and microphone adapters.
- `randomiser.pipeline`: feature extraction, health checks, source fusion, conditioning, OTP generation, and orchestration.
- `randomiser.io`: experiment folder creation, source input saving, manifest writing, and output CSV writing.
- `randomiser.modes`: batch and web backend mode functions.
- `randomiser.cli`: terminal commands and script entrypoints.

Batch mode calls the same pipeline functions that web mode will call. CLI and web code should not duplicate feature extraction, health logic, fusion, conditioning, or storage logic.

The storage boundary is `randomiser.io`. Raw source bytes are written through IO helpers so every run keeps source inputs and OTP output tied to the same `run_id`.

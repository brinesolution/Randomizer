# Architecture

Randomiser uses a `src/` layout and separates seed creation from output
generation.

Core packages:

- `randomiser.core`: enums, dataclasses, configuration, paths, timing, hashing,
  and shared exceptions.
- `randomiser.sources`: laptop source collectors and registry.
- `randomiser.integrations`: camera and microphone hardware adapters.
- `randomiser.pipeline`: feature extraction, health gating, source fusion,
  conditioning, and reusable master-seed creation.
- `randomiser.generators`: domain-separated OTP, map, and maze generators.
- `randomiser.io`: source input, seed index, manifest, and generated-output
  storage.
- `randomiser.modes`: batch and web backend workflows.
- `randomiser.trace`: display-ready source and seed-creation visual data.
- `randomiser.cli`: terminal commands and script entry points.

The central boundary is:

```text
EntropyManager -> SeedRunResult -> selected output generator
```

`EntropyManager` never generates an OTP, map, or maze. It stops after final
conditioning and returns a 512-bit seed. Output generators derive isolated
child seeds and can run repeatedly without recollecting sources.

Both batch and web mode use the same pipeline and storage contracts.

Randomiser is an experimental entropy collection and procedural generation
system.

It is not:

- a certified hardware random number generator,
- a certified true random number generator,
- a production seed or generated-output service,
- a replacement for audited cryptographic products.

Known limitations:

- Camera and microphone output depends on device permissions and local environment.
- Timing jitter depends on the operating system, scheduler, load, CPU power state, and background processes.
- MVP health tests reject obvious failures but do not prove entropy quality.
- Experiment input folders may contain private raw sensor data and timing data.
- Generated maps and mazes are deterministic demonstrations, not simulation-grade procedural generation.

Use the project for controlled experiments, demos, and learning. Do not use it to protect real accounts, money, secrets, or production systems.

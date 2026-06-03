Randomiser is a research and portfolio prototype.

It is not:

- a certified hardware random number generator,
- a certified true random number generator,
- a production OTP system,
- a replacement for audited cryptographic products.

Known limitations:

- Camera and microphone output depends on device permissions and local environment.
- Timing jitter depends on the operating system, scheduler, load, CPU power state, and background processes.
- MVP health tests reject obvious failures but do not prove entropy quality.
- Experiment input folders may contain private raw sensor data and timing data.
- The web UI is planned after backend stabilization and must reuse the same backend pipeline.

Use the project for controlled experiments, demos, and learning. Do not use it to protect real accounts, money, secrets, or production systems.

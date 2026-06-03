The MVP sources are laptop-local inputs:

- Camera: captures one frame through OpenCV, converts to grayscale when needed, and extracts low bits.
- Microphone: records a short PCM block through sounddevice and extracts low bits from sample deltas.
- CPU jitter: measures small timing deltas around CPU work.
- Scheduler jitter: measures timing deltas across yielding worker threads.
- OS random baseline: uses `os.urandom` as a comparison source, not as the main project identity.

Camera and microphone tests use the real laptop devices. A missing device or permission failure is treated as a real failure for those tests.

Limitations:

- Laptop sensors and timing are affected by drivers, OS scheduling, power state, lighting, room noise, and permissions.
- The MVP health checks are broad sanity checks, not formal entropy certification.
- Raw source bytes are private experiment data and should not be committed.

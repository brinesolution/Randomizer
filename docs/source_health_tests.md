Source health checks reject obviously broken source bytes before fusion.

Current checks:

- Data must be non-empty.
- Data must not be one constant byte value.
- Unique byte count must meet a minimum threshold.
- Bit balance must stay within a broad range.
- Shannon entropy estimate must meet a broad minimum threshold.

The health gate returns:

- `pass`: source can be used.
- `warn`: reserved for accepted-but-suspicious behavior in later stages.
- `fail`: source is excluded from fusion.

Run status is decided from source health:

- `ok`: all enabled sources pass.
- `degraded`: enough sources pass to continue, but at least one source failed.
- `failed`: fewer than the configured minimum sources pass.

These checks are for MVP safety and debugging. They are not a statistical test suite.

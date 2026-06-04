# OTP Generation

OTP generation is an optional output selected after the master seed is saved.
It is no longer part of the source entropy pipeline.

Flow:

1. Derive an OTP-specific child seed from the master seed.
2. Read 32-bit candidates from the child seed.
3. Accept only candidates below the largest evenly divisible limit.
4. Reduce the accepted candidate into the six-digit range.
5. Format the value with leading zeros preserved.

The domain-separated child seed prevents OTP generation from changing map or
maze output. Rejection sampling avoids the bias caused by applying simple
modulo to every 32-bit candidate.

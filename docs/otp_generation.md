OTP generation starts only after source health gating.

Current flow:

1. Accepted source bytes are independently hashed.
2. Source hashes are fused in stable source-name order.
3. Fused bytes are conditioned with SHA-512.
4. The conditioned digest is converted to an integer with rejection sampling.
5. The integer is formatted as exactly six digits.

Rejection sampling avoids the simple modulo shortcut. A 32-bit chunk is accepted only when it falls below the largest multiple of the target range that fits inside `2**32`. If a chunk is rejected, the next chunk is tried. If all chunks are exhausted, the digest is rehashed with a counter.

Formatting preserves leading zeros, so value `42` becomes `000042`.

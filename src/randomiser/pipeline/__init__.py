from __future__ import annotations

from randomiser.pipeline.degraded_mode import count_passed_sources, decide_run_status
from randomiser.pipeline.conditioner import condition_fused_bytes
from randomiser.pipeline.features import (
    calculate_bit_balance,
    estimate_lag1_autocorrelation,
    estimate_shannon_entropy,
    extract_features,
)
from randomiser.pipeline.hg_msef import fuse_healthy_sources, fuse_source_hashes
from randomiser.pipeline.health_gate import (
    evaluate_source_health,
    evaluate_sources,
    passed_sources,
)
from randomiser.pipeline.health_tests import run_health_tests
from randomiser.pipeline.otp_generator import (
    format_otp,
    generate_otp_from_digest,
    generate_six_digit_otp,
)
from randomiser.pipeline.rejection_sampling import rejection_sample_int
from randomiser.pipeline.source_hasher import hash_source_sample

__all__ = [
    "calculate_bit_balance",
    "condition_fused_bytes",
    "count_passed_sources",
    "decide_run_status",
    "estimate_lag1_autocorrelation",
    "estimate_shannon_entropy",
    "evaluate_source_health",
    "evaluate_sources",
    "extract_features",
    "format_otp",
    "fuse_healthy_sources",
    "fuse_source_hashes",
    "generate_otp_from_digest",
    "generate_six_digit_otp",
    "hash_source_sample",
    "passed_sources",
    "rejection_sample_int",
    "run_health_tests",
]

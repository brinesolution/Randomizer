from __future__ import annotations

from randomiser.pipeline.degraded_mode import count_passed_sources, decide_run_status
from randomiser.pipeline.conditioner import condition_fused_bytes
from randomiser.pipeline.calibration import calibrate_sources
from randomiser.pipeline.entropy_manager import EntropyManager, generate_once
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
from randomiser.pipeline.parallel_collector import CollectionResult, collect_sources
from randomiser.pipeline.rejection_sampling import rejection_sample_int
from randomiser.pipeline.run_context import RunContext, build_run_context, config_digest
from randomiser.pipeline.source_hasher import hash_source_sample
from randomiser.pipeline.warmup import check_source_availability, unavailable_sources

__all__ = [
    "calculate_bit_balance",
    "calibrate_sources",
    "check_source_availability",
    "CollectionResult",
    "condition_fused_bytes",
    "config_digest",
    "count_passed_sources",
    "decide_run_status",
    "collect_sources",
    "EntropyManager",
    "estimate_lag1_autocorrelation",
    "estimate_shannon_entropy",
    "evaluate_source_health",
    "evaluate_sources",
    "extract_features",
    "format_otp",
    "fuse_healthy_sources",
    "fuse_source_hashes",
    "generate_otp_from_digest",
    "generate_once",
    "generate_six_digit_otp",
    "hash_source_sample",
    "passed_sources",
    "rejection_sample_int",
    "RunContext",
    "build_run_context",
    "run_health_tests",
    "unavailable_sources",
]

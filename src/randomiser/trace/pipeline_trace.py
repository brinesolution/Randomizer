from __future__ import annotations

from randomiser.core.models import SeedRunResult
from randomiser.trace.step_models import TraceStepView


def build_pipeline_trace(result: SeedRunResult) -> list[TraceStepView]:
    healthy_count = sum(1 for health in result.health.values() if health.status.value == "pass")
    return [
        TraceStepView(
            1,
            "sources requested",
            "ok",
            "camera, microphone, cpu jitter, and scheduler jitter were requested by the web flow",
            {"run_id": result.run_id},
        ),
        TraceStepView(
            2,
            "source collection",
            result.status.value,
            "raw source bytes were collected and saved with one shared run id",
            {"source_files": dict(result.source_files)},
        ),
        TraceStepView(
            3,
            "feature extraction",
            "ok",
            "byte count, bit balance, unique byte count, entropy, and autocorrelation were computed",
            {"feature_count": len(result.features)},
        ),
        TraceStepView(
            4,
            "health gate",
            result.status.value,
            "sources were checked before being accepted for fusion",
            {"healthy_sources": healthy_count, "total_sources": len(result.health)},
        ),
        TraceStepView(
            5,
            "source hashing",
            "ok" if result.seed_hex else result.status.value,
            "accepted source bytes were hashed independently with source identity and metadata",
            {"accepted_hashes": healthy_count},
        ),
        TraceStepView(
            6,
            "hg-msef fusion",
            "ok" if result.seed_hex else result.status.value,
            "accepted source hashes were sorted by source name and fused with run context",
            {"mode": result.mode.value},
        ),
        TraceStepView(
            7,
            "conditioning",
            "ok" if result.seed_hex else result.status.value,
            "fused bytes were conditioned with SHA-512 into a reusable master seed",
            {},
        ),
        TraceStepView(
            8,
            "master seed",
            result.status.value,
            "the reusable 512-bit seed is ready for an OTP, map, or maze",
            {"seed_bytes": len(result.seed_hex) // 2 if result.seed_hex else 0},
        ),
    ]

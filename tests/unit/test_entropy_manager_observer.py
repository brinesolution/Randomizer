from __future__ import annotations

from randomiser.core.enums import RunMode
from randomiser.pipeline.entropy_manager import EntropyManager
from randomiser.pipeline.run_context import build_run_context
from randomiser.sources import CPUJitterSource, SchedulerJitterSource


def test_entropy_manager_emits_completed_pipeline_stages() -> None:
    events: list[str] = []
    context = build_run_context(
        1,
        mode=RunMode.WEB,
        experiment_id="exp_observer",
        config={"sources": ["cpu_jitter", "scheduler_jitter"]},
    )
    manager = EntropyManager(
        [CPUJitterSource(iterations=64), SchedulerJitterSource(thread_count=2, samples_per_thread=16)],
        min_required_sources=1,
    )

    result, samples = manager.generate_once_with_samples(
        context,
        observer=lambda stage, payload: events.append(stage),
    )

    assert len(samples) == 2
    assert result.otp
    assert events == [
        "source_collection",
        "source_analysis",
        "health_gate",
        "fusion",
        "conditioning",
        "otp_generation",
    ]

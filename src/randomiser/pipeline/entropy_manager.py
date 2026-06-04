from __future__ import annotations

from collections.abc import Iterable
from collections.abc import Callable
from typing import Any

from randomiser.core.constants import DEFAULT_MIN_HEALTHY_SOURCES
from randomiser.core.enums import HealthStatus, RunMode, RunStatus
from randomiser.core.models import HealthResult, PipelineTraceStep, SeedRunResult, SourceFeatures
from randomiser.pipeline.conditioner import condition_fused_bytes
from randomiser.pipeline.degraded_mode import decide_run_status
from randomiser.pipeline.features import extract_features
from randomiser.pipeline.health_gate import evaluate_source_health
from randomiser.pipeline.hg_msef import fuse_healthy_sources
from randomiser.pipeline.parallel_collector import CollectionResult, collect_sources
from randomiser.pipeline.run_context import RunContext
from randomiser.sources.base import EntropySource

StageObserver = Callable[[str, dict[str, Any]], None]


def _notify(observer: StageObserver | None, stage: str, payload: dict[str, Any]) -> None:
    if observer is not None:
        observer(stage, payload)


class EntropyManager:
    def __init__(
        self,
        sources: Iterable[EntropySource],
        *,
        min_required_sources: int = DEFAULT_MIN_HEALTHY_SOURCES,
    ) -> None:
        self.sources = list(sources)
        self.min_required_sources = min_required_sources

    def generate_once(self, context: RunContext, *, observer: StageObserver | None = None) -> SeedRunResult:
        collection = collect_sources(self.sources, context.run_id)
        _notify(
            observer,
            "source_collection",
            {"source_count": len(collection.samples), "errors": dict(collection.errors)},
        )
        return self.generate_from_collection(context, collection, observer=observer)

    def generate_once_with_samples(self, context: RunContext, *, observer: StageObserver | None = None):
        collection = collect_sources(self.sources, context.run_id)
        _notify(
            observer,
            "source_collection",
            {"source_count": len(collection.samples), "errors": dict(collection.errors)},
        )
        return self.generate_from_collection(context, collection, observer=observer), collection.samples

    def generate_from_collection(
        self,
        context: RunContext,
        collection: CollectionResult,
        *,
        observer: StageObserver | None = None,
    ) -> SeedRunResult:
        features: dict[str, SourceFeatures] = {}
        health: dict[str, HealthResult] = {}
        trace: list[PipelineTraceStep] = []

        trace.append(
            PipelineTraceStep(
                name="source_collection",
                status=RunStatus.OK if not collection.errors else RunStatus.DEGRADED,
                message=f"collected {len(collection.samples)} source samples",
                metrics={"errors": dict(collection.errors)},
            )
        )

        for sample in collection.samples:
            source_features = extract_features(sample)
            source_health = evaluate_source_health(sample, source_features)
            features[sample.source_name.value] = source_features
            health[sample.source_name.value] = source_health

        for source_name, message in collection.errors.items():
            health[source_name] = HealthResult(
                source_name=next(source.name for source in self.sources if source.name.value == source_name),
                status=HealthStatus.FAIL,
                score=0.0,
                reasons=[f"collection failed: {message}"],
            )

        _notify(
            observer,
            "source_analysis",
            {"feature_count": len(features), "health_count": len(health)},
        )
        run_status = decide_run_status(health.values(), min_required_sources=self.min_required_sources)
        trace.append(
            PipelineTraceStep(
                name="health_gate",
                status=run_status,
                message=f"{sum(1 for item in health.values() if item.status is HealthStatus.PASS)} healthy sources",
                metrics={"min_required_sources": self.min_required_sources},
            )
        )
        _notify(
            observer,
            "health_gate",
            {
                "status": run_status.value,
                "healthy_sources": sum(1 for item in health.values() if item.status is HealthStatus.PASS),
                "total_sources": len(health),
            },
        )

        seed_hex = ""
        if run_status is not RunStatus.FAILED:
            fused = fuse_healthy_sources(
                collection.samples,
                health,
                run_id=context.run_id,
                context={
                    "experiment_id": context.experiment_id,
                    "mode": context.mode.value,
                    "config_hash": context.config_hash,
                },
            )
            _notify(observer, "fusion", {"digest": fused.hex(), "byte_count": len(fused)})
            conditioned = condition_fused_bytes(
                fused,
                run_id=context.run_id,
                context={
                    "experiment_id": context.experiment_id,
                    "mode": context.mode.value,
                    "config_hash": context.config_hash,
                },
            )
            _notify(observer, "conditioning", {"digest": conditioned.hex(), "byte_count": len(conditioned)})
            seed_hex = conditioned.hex()
            _notify(observer, "seed_generation", {"seed": seed_hex, "byte_count": len(conditioned)})
            trace.extend(
                [
                    PipelineTraceStep("source_fusion", RunStatus.OK, "fused healthy source hashes"),
                    PipelineTraceStep("conditioning", RunStatus.OK, "conditioned fused bytes"),
                    PipelineTraceStep("seed_generation", RunStatus.OK, "created reusable master seed"),
                ]
            )

        return SeedRunResult(
            run_id=context.run_id,
            mode=context.mode,
            seed_hex=seed_hex,
            status=run_status,
            health=health,
            features=features,
            trace=trace,
            created_at=context.created_at,
        )


def generate_once(
    sources: Iterable[EntropySource],
    context: RunContext,
    *,
    min_required_sources: int = DEFAULT_MIN_HEALTHY_SOURCES,
) -> SeedRunResult:
    return EntropyManager(sources, min_required_sources=min_required_sources).generate_once(context)

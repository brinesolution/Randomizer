from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable

import numpy as np

from randomiser.core.constants import DEFAULT_MIN_HEALTHY_SOURCES
from randomiser.core.enums import RunMode, SourceName
from randomiser.core.models import ExperimentManifest
from randomiser.core.paths import get_experiments_dir
from randomiser.io.experiment_store import create_experiment_structure
from randomiser.io.manifest_writer import write_manifest
from randomiser.io.run_logger import log_run
from randomiser.pipeline.entropy_manager import EntropyManager
from randomiser.pipeline.health_tests import (
    DEFAULT_MAX_BIT_BALANCE,
    DEFAULT_MIN_BIT_BALANCE,
    DEFAULT_MIN_ENTROPY,
    DEFAULT_MIN_UNIQUE_BYTES,
)
from randomiser.pipeline.run_context import build_run_context
from randomiser.pipeline.source_hasher import hash_source_sample
from randomiser.sources import CameraSource, CPUJitterSource, MicrophoneSource, SchedulerJitterSource
from randomiser.trace.pipeline_trace import build_pipeline_trace
from randomiser.trace.web_visuals import (
    build_sample_visual,
    build_transformation_visual,
    compact_series,
    save_camera_previews,
    save_microphone_preview,
)

EventEmitter = Callable[[dict[str, Any]], None]


def build_web_sources():
    return [
        CameraSource(),
        MicrophoneSource(duration_ms=1000),
        CPUJitterSource(iterations=512),
        SchedulerJitterSource(thread_count=2, samples_per_thread=128),
    ]


def source_check_summary(features):
    return [
        {"name": "non-empty bytes", "passed": features.byte_count > 0},
        {"name": "not constant", "passed": features.unique_byte_count > 1},
        {"name": "minimum unique bytes", "passed": features.unique_byte_count >= DEFAULT_MIN_UNIQUE_BYTES},
        {
            "name": "bit balance range",
            "passed": DEFAULT_MIN_BIT_BALANCE <= features.bit_balance <= DEFAULT_MAX_BIT_BALANCE,
        },
        {"name": "entropy minimum", "passed": features.entropy_estimate >= DEFAULT_MIN_ENTROPY},
    ]


def artifact_url(experiment_id: str, relative_path: str) -> str:
    return f"/artifacts/{experiment_id}/{relative_path}"


def source_evidence(source, experiment_dir, experiment_id: str, run_id: str) -> dict[str, Any]:
    if isinstance(source, CameraSource) and source.last_frame is not None:
        paths = save_camera_previews(
            experiment_dir,
            run_id,
            source.last_frame,
            bit_count=source.bit_count,
        )
        return {
            "kind": "camera",
            "images": {name: artifact_url(experiment_id, path) for name, path in paths.items()},
        }
    if isinstance(source, MicrophoneSource) and source.last_samples is not None:
        audio_path = save_microphone_preview(
            experiment_dir,
            run_id,
            source.last_samples,
            sample_rate=source.sample_rate,
        )
        samples = source.last_samples.astype(np.int64)
        deltas = np.diff(samples, append=samples[-1])
        return {
            "kind": "microphone",
            "audio": artifact_url(experiment_id, audio_path),
            "originalSeries": compact_series(samples),
            "deltaSeries": compact_series(deltas),
            "sampleRate": source.sample_rate,
            "durationMs": source.duration_ms,
        }
    if isinstance(source, CPUJitterSource):
        return {
            "kind": "cpu_jitter",
            "timingSeries": compact_series(source.last_deltas),
            "lowByteSeries": compact_series([value & 0xFF for value in source.last_deltas]),
        }
    if isinstance(source, SchedulerJitterSource):
        return {
            "kind": "scheduler_jitter",
            "timingSeries": compact_series(source.last_deltas),
            "threadLanes": [compact_series(values, 64) for values in source.last_thread_deltas],
            "lowByteSeries": compact_series([value & 0xFF for value in source.last_deltas]),
        }
    return {"kind": "missing"}


def serialize_run(emit: EventEmitter | None = None):
    def publish(event: dict[str, Any]) -> None:
        if emit is not None:
            emit(event)

    sources = build_web_sources()
    experiment_id = f"exp_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_web"
    experiments_root = get_experiments_dir()
    experiment_dir = create_experiment_structure(
        experiments_root,
        experiment_id,
        source_names=[source.name for source in sources],
    )
    write_manifest(
        experiment_dir,
        ExperimentManifest(
            experiment_id=experiment_id,
            mode=RunMode.WEB,
            config_name="web_mode",
            started_at=datetime.now(timezone.utc),
            source_names=[source.name for source in sources],
        ),
    )

    context = build_run_context(
        1,
        mode=RunMode.WEB,
        experiment_id=experiment_id,
        config={"sources": [source.name.value for source in sources]},
    )
    result, samples = EntropyManager(
        sources,
        min_required_sources=DEFAULT_MIN_HEALTHY_SOURCES,
    ).generate_once_with_samples(
        context,
        observer=lambda stage, payload: publish(
            {"type": "stage", "stage": stage, "payload": payload}
        ),
    )
    result = log_run(experiment_dir, result, samples)

    samples_by_name = {sample.source_name.value: sample for sample in samples}
    sources_by_name = {source.name.value: source for source in sources}
    source_payload = []
    for source_name in [SourceName.CAMERA, SourceName.MICROPHONE, SourceName.CPU_JITTER, SourceName.SCHEDULER_JITTER]:
        key = source_name.value
        features = result.features.get(key)
        health = result.health.get(key)
        sample = samples_by_name.get(key)
        source = sources_by_name[key]
        source_payload.append(
            {
                "name": key,
                "label": key.replace("_", " ").upper(),
                "requested": True,
                "collected": sample is not None,
                "byteCount": features.byte_count if features else 0,
                "uniqueBytes": features.unique_byte_count if features else 0,
                "bitBalance": round(features.bit_balance, 4) if features else 0,
                "entropy": round(features.entropy_estimate, 4) if features else 0,
                "autocorrelation": round(features.autocorrelation, 4) if features else 0,
                "health": health.status.value if health else "missing",
                "score": round(health.score, 4) if health else 0,
                "reasons": health.reasons if health else ["not collected"],
                "checks": source_check_summary(features) if features else [],
                "inputFile": result.source_files.get(key, ""),
                "hashPreview": hash_source_sample(sample).hex()[:16] if sample else "",
                "visual": build_sample_visual(sample) if sample else {},
                "evidence": source_evidence(source, experiment_dir, experiment_id, result.run_id),
            }
        )

    pipeline_context = {
        "experiment_id": context.experiment_id,
        "mode": context.mode.value,
        "config_hash": context.config_hash,
    }
    transformation = (
        build_transformation_visual(
            samples,
            result.health,
            run_id=result.run_id,
            context=pipeline_context,
        )
        if result.otp
        else {}
    )
    payload = {
        "ok": True,
        "runId": result.run_id,
        "status": result.status.value,
        "otp": result.otp,
        "experimentId": experiment_id,
        "experimentPath": str(experiment_dir),
        "outputIndex": str(experiment_dir / "output" / "run_index.csv"),
        "sources": source_payload,
        "trace": [asdict(step) for step in build_pipeline_trace(result)],
        "transformation": transformation,
        "thresholds": {
            "minimumUniqueBytes": DEFAULT_MIN_UNIQUE_BYTES,
            "minimumEntropy": DEFAULT_MIN_ENTROPY,
            "minimumBitBalance": DEFAULT_MIN_BIT_BALANCE,
            "maximumBitBalance": DEFAULT_MAX_BIT_BALANCE,
        },
    }
    publish(
        {
            "type": "stage",
            "stage": "experiment_save",
            "payload": {"experimentPath": str(experiment_dir), "outputIndex": payload["outputIndex"]},
        }
    )
    publish({"type": "result", "payload": payload})
    return payload


def main() -> None:
    stream = "--stream" in sys.argv

    def emit(event: dict[str, Any]) -> None:
        print(json.dumps(event, sort_keys=True), flush=True)

    try:
        result = serialize_run(emit=emit if stream else None)
        if not stream:
            print(json.dumps(result, sort_keys=True))
    except Exception as exc:
        error = {"type": "error", "error": str(exc)} if stream else {"ok": False, "error": str(exc)}
        print(json.dumps(error, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

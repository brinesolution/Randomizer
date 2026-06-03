from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone

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


def build_web_sources():
    return [
        CameraSource(),
        MicrophoneSource(duration_ms=50),
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


def serialize_run():
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
    ).generate_once_with_samples(context)
    result = log_run(experiment_dir, result, samples)

    samples_by_name = {sample.source_name.value: sample for sample in samples}
    source_payload = []
    for source_name in [SourceName.CAMERA, SourceName.MICROPHONE, SourceName.CPU_JITTER, SourceName.SCHEDULER_JITTER]:
        key = source_name.value
        features = result.features.get(key)
        health = result.health.get(key)
        sample = samples_by_name.get(key)
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
            }
        )

    return {
        "ok": True,
        "runId": result.run_id,
        "status": result.status.value,
        "otp": result.otp,
        "experimentId": experiment_id,
        "experimentPath": str(experiment_dir),
        "outputIndex": str(experiment_dir / "output" / "run_index.csv"),
        "sources": source_payload,
        "trace": [asdict(step) for step in build_pipeline_trace(result)],
    }


def main() -> None:
    try:
        print(json.dumps(serialize_run(), sort_keys=True))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))


if __name__ == "__main__":
    main()

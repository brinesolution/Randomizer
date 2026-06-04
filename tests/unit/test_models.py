from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from randomiser.core.constants import (
    DEFAULT_MIN_HEALTHY_SOURCES,
    OTP_DIGITS,
    OTP_RANGE,
    SOURCE_FOLDER_NAMES,
)
from randomiser.core.enums import HealthStatus, RunMode, RunStatus, SourceName
from randomiser.core.exceptions import (
    ConfigError,
    ExperimentStorageError,
    HealthGateError,
    RandomiserError,
    SourceCollectionError,
)
from randomiser.core.hashing import blake2b_digest, sha512_digest
from randomiser.core.models import (
    ExperimentManifest,
    HealthResult,
    PipelineTraceStep,
    SeedRunResult,
    SourceFeatures,
    SourceSample,
)
from randomiser.core.paths import (
    get_config_dir,
    get_data_dir,
    get_experiments_dir,
    get_project_root,
)
from randomiser.core.timing import duration_ms, utc_now, utc_now_iso


def test_source_sample_and_features_models_store_expected_values() -> None:
    collected_at = datetime(2026, 6, 4, tzinfo=timezone.utc)
    sample = SourceSample(
        source_name=SourceName.CPU_JITTER,
        run_id="run_000001",
        raw_bytes=b"\x01\x02\x03",
        collected_at=collected_at,
        duration_ms=4.5,
        metadata={"iterations": 3},
    )
    features = SourceFeatures(
        source_name=SourceName.CPU_JITTER,
        byte_count=3,
        bit_balance=0.5,
        entropy_estimate=1.58,
        unique_byte_count=3,
        autocorrelation=0.1,
        extra={"iterations": 3},
    )

    assert sample.source_name is SourceName.CPU_JITTER
    assert sample.run_id == "run_000001"
    assert sample.raw_bytes == b"\x01\x02\x03"
    assert features.byte_count == 3
    assert features.extra["iterations"] == 3


def test_health_trace_result_and_manifest_models_have_stable_defaults() -> None:
    health = HealthResult(
        source_name=SourceName.CAMERA,
        status=HealthStatus.PASS,
        score=0.91,
        reasons=[],
    )
    trace = PipelineTraceStep(
        name="source_collection",
        status=RunStatus.OK,
        message="collected source bytes",
        input_ref="input/camera/run_000001.bin",
        output_ref="trace/source_collection.json",
        metrics={"byte_count": 128},
    )
    result = SeedRunResult(
        run_id="run_000001",
        mode=RunMode.BATCH,
        seed_hex="ab" * 64,
        status=RunStatus.OK,
        source_files={"camera": "input/camera/run_000001.bin"},
        health={"camera": health},
        features={},
        trace=[trace],
        created_at=utc_now(),
    )
    manifest = ExperimentManifest(
        experiment_id="exp_0001",
        mode=RunMode.BATCH,
        config_name="batch_run.yaml",
        started_at=utc_now(),
        source_names=[SourceName.CAMERA, SourceName.CPU_JITTER],
    )

    assert result.seed_hex == "ab" * 64
    assert result.trace[0].name == "source_collection"
    assert manifest.source_names == [SourceName.CAMERA, SourceName.CPU_JITTER]
    assert asdict(manifest)["config_name"] == "batch_run.yaml"


def test_core_enums_constants_and_exceptions_are_defined_for_stage_one() -> None:
    assert SourceName.MICROPHONE.value == "microphone"
    assert RunMode.WEB.value == "web"
    assert RunStatus.DEGRADED.value == "degraded"
    assert HealthStatus.FAIL.value == "fail"
    assert OTP_RANGE == 1_000_000
    assert OTP_DIGITS == 6
    assert DEFAULT_MIN_HEALTHY_SOURCES == 2
    assert SOURCE_FOLDER_NAMES[SourceName.SCHEDULER_JITTER] == "scheduler_jitter"
    assert issubclass(ConfigError, RandomiserError)
    assert issubclass(SourceCollectionError, RandomiserError)
    assert issubclass(HealthGateError, RandomiserError)
    assert issubclass(ExperimentStorageError, RandomiserError)


def test_path_hashing_and_timing_helpers_work_for_stage_one() -> None:
    project_root = get_project_root()
    assert project_root == Path("E:/Randomiser")
    assert get_config_dir() == project_root / "config"
    assert get_data_dir() == project_root / "data"
    assert get_experiments_dir() == project_root / "data" / "experiments"

    payload = b"randomiser"
    sha_digest = sha512_digest(payload)
    blake_digest = blake2b_digest(payload)
    assert len(sha_digest) == 64
    assert len(blake_digest) == 64

    start = 1_000_000
    end = 2_500_000
    assert duration_ms(start, end) == 1.5
    assert utc_now().tzinfo == timezone.utc
    assert utc_now_iso().endswith("Z")

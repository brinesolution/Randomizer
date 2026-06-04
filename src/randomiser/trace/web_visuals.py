from __future__ import annotations

import wave
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from randomiser.core.enums import HealthStatus
from randomiser.core.models import HealthResult, SourceSample
from randomiser.pipeline.conditioner import condition_fused_bytes
from randomiser.pipeline.hg_msef import fuse_source_hashes
from randomiser.pipeline.source_hasher import hash_source_sample

def compact_series(values: Sequence[int] | np.ndarray, limit: int = 128) -> list[int]:
    items = [int(value) for value in values]
    if len(items) <= limit:
        return items
    indexes = np.linspace(0, len(items) - 1, limit, dtype=int)
    return [items[index] for index in indexes]


def byte_histogram(raw_bytes: bytes) -> list[dict[str, int | str]]:
    counts = Counter(byte // 16 for byte in raw_bytes)
    return [
        {
            "label": f"{group * 16:02x}-{group * 16 + 15:02x}",
            "count": counts.get(group, 0),
        }
        for group in range(16)
    ]


def build_sample_visual(sample: SourceSample) -> dict[str, Any]:
    lag_source = compact_series(sample.raw_bytes, 65)
    return {
        "series": compact_series(sample.raw_bytes),
        "histogram": byte_histogram(sample.raw_bytes),
        "lagPairs": [
            {"x": previous, "y": next_value}
            for previous, next_value in zip(lag_source[:-1], lag_source[1:], strict=True)
        ],
        "hexPreview": " ".join(f"{byte:02x}" for byte in sample.raw_bytes[:32]),
        "metadata": dict(sample.metadata),
    }


def save_camera_previews(
    experiment_dir: Path,
    run_id: str,
    frame: np.ndarray,
    *,
    bit_count: int = 2,
) -> dict[str, str]:
    import cv2

    preview_dir = experiment_dir / "output" / "previews" / "camera"
    preview_dir.mkdir(parents=True, exist_ok=True)
    original_path = preview_dir / f"{run_id}_original.jpg"
    grayscale_path = preview_dir / f"{run_id}_grayscale.png"
    low_bits_path = preview_dir / f"{run_id}_low_bits.png"

    array = np.asarray(frame)
    grayscale = array.mean(axis=2).astype(np.uint8) if array.ndim == 3 else array.astype(np.uint8)
    mask = (1 << bit_count) - 1
    low_bits = ((grayscale & mask) * (255 // mask)).astype(np.uint8)

    if not cv2.imwrite(str(original_path), array):
        raise OSError(f"could not write camera preview: {original_path}")
    if not cv2.imwrite(str(grayscale_path), grayscale):
        raise OSError(f"could not write camera preview: {grayscale_path}")
    if not cv2.imwrite(str(low_bits_path), low_bits):
        raise OSError(f"could not write camera preview: {low_bits_path}")

    return {
        "original": original_path.relative_to(experiment_dir).as_posix(),
        "grayscale": grayscale_path.relative_to(experiment_dir).as_posix(),
        "lowBits": low_bits_path.relative_to(experiment_dir).as_posix(),
    }


def save_microphone_preview(
    experiment_dir: Path,
    run_id: str,
    samples: np.ndarray,
    *,
    sample_rate: int,
) -> str:
    preview_dir = experiment_dir / "output" / "previews" / "microphone"
    preview_dir.mkdir(parents=True, exist_ok=True)
    audio_path = preview_dir / f"{run_id}.wav"
    pcm = np.asarray(samples, dtype=np.int16).ravel()
    with wave.open(str(audio_path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(pcm.tobytes())
    return audio_path.relative_to(experiment_dir).as_posix()


def build_transformation_visual(
    samples: Sequence[SourceSample],
    health_results: Mapping[str, HealthResult],
    *,
    run_id: str,
    context: Mapping[str, Any],
) -> dict[str, Any]:
    accepted = {HealthStatus.PASS, HealthStatus.WARN}
    samples_by_name = {sample.source_name: sample for sample in samples}
    hashes = {
        sample.source_name: hash_source_sample(sample)
        for sample in samples
        if health_results.get(sample.source_name.value)
        and health_results[sample.source_name.value].status in accepted
    }
    fused = fuse_source_hashes(hashes, run_id=run_id, context=context)
    conditioned = condition_fused_bytes(fused, run_id=run_id, context=context)
    return {
        "sourceHashes": [
            {
                "source": source_name.value,
                "rawPreview": list(samples_by_name[source_name].raw_bytes[:16]),
                "digest": digest.hex(),
            }
            for source_name, digest in sorted(hashes.items(), key=lambda item: item[0].value)
        ],
        "fusedDigest": fused.hex(),
        "conditionedDigest": conditioned.hex(),
        "seedHex": conditioned.hex(),
    }

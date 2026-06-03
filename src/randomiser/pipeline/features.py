from __future__ import annotations

from collections import Counter
from math import log2, sqrt

from randomiser.core.models import SourceFeatures, SourceSample


def calculate_bit_balance(raw_bytes: bytes) -> float:
    if not raw_bytes:
        return 0.0

    one_bits = sum(byte.bit_count() for byte in raw_bytes)
    return one_bits / (len(raw_bytes) * 8)


def estimate_shannon_entropy(raw_bytes: bytes) -> float:
    if not raw_bytes:
        return 0.0

    total = len(raw_bytes)
    counts = Counter(raw_bytes)
    return sum(-(count / total) * log2(count / total) for count in counts.values())


def estimate_lag1_autocorrelation(raw_bytes: bytes) -> float:
    if len(raw_bytes) < 2:
        return 0.0

    previous_values = raw_bytes[:-1]
    next_values = raw_bytes[1:]
    sample_count = len(previous_values)
    previous_mean = sum(previous_values) / sample_count
    next_mean = sum(next_values) / sample_count

    numerator = sum(
        (previous - previous_mean) * (next_value - next_mean)
        for previous, next_value in zip(previous_values, next_values, strict=True)
    )
    previous_variance = sum((previous - previous_mean) ** 2 for previous in previous_values)
    next_variance = sum((next_value - next_mean) ** 2 for next_value in next_values)
    denominator = sqrt(previous_variance * next_variance)

    if denominator == 0.0:
        return 0.0

    return numerator / denominator


def extract_features(sample: SourceSample) -> SourceFeatures:
    raw_bytes = sample.raw_bytes
    return SourceFeatures(
        source_name=sample.source_name,
        byte_count=len(raw_bytes),
        bit_balance=calculate_bit_balance(raw_bytes),
        entropy_estimate=estimate_shannon_entropy(raw_bytes),
        unique_byte_count=len(set(raw_bytes)),
        autocorrelation=estimate_lag1_autocorrelation(raw_bytes),
        extra=dict(sample.metadata),
    )

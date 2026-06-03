from __future__ import annotations

import pytest

from randomiser.pipeline.rejection_sampling import rejection_sample_int


def test_rejection_sampling_returns_value_inside_range() -> None:
    value = rejection_sample_int(b"\x00\x0f\x42\x3f", upper_bound=1_000_000)

    assert 0 <= value < 1_000_000


def test_rejection_sampling_rejects_out_of_range_chunks() -> None:
    upper_bound = 10
    limit = (2**32 // upper_bound) * upper_bound
    rejected_chunk = limit.to_bytes(4, "big")
    accepted_chunk = (7).to_bytes(4, "big")

    assert rejection_sample_int(rejected_chunk + accepted_chunk, upper_bound=upper_bound) == 7


def test_rejection_sampling_rejects_invalid_upper_bound() -> None:
    with pytest.raises(ValueError):
        rejection_sample_int(b"\x00\x00\x00\x01", upper_bound=0)

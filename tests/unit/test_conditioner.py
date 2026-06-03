from __future__ import annotations

from randomiser.pipeline.conditioner import condition_fused_bytes


def test_conditioner_returns_stable_64_byte_digest() -> None:
    first = condition_fused_bytes(b"fused-bytes", run_id="run_000001")
    second = condition_fused_bytes(b"fused-bytes", run_id="run_000001")

    assert first == second
    assert len(first) == 64


def test_conditioner_changes_with_input_or_context() -> None:
    base = condition_fused_bytes(b"fused-bytes", run_id="run_000001")

    assert base != condition_fused_bytes(b"changed", run_id="run_000001")
    assert base != condition_fused_bytes(b"fused-bytes", run_id="run_000002")

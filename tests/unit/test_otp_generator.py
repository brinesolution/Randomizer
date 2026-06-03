from __future__ import annotations

import pytest

from randomiser.pipeline.otp_generator import format_otp, generate_otp_from_digest


def test_format_otp_preserves_leading_zeros() -> None:
    assert format_otp(42) == "000042"


def test_format_otp_rejects_values_outside_six_digit_range() -> None:
    with pytest.raises(ValueError):
        format_otp(1_000_000)

    with pytest.raises(ValueError):
        format_otp(-1)


def test_generate_otp_from_digest_returns_six_digits() -> None:
    otp = generate_otp_from_digest(b"\x00\x00\x00*")

    assert otp == "000042"
    assert len(otp) == 6
    assert otp.isdigit()

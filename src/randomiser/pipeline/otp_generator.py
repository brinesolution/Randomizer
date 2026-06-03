from __future__ import annotations

from randomiser.core.constants import OTP_DIGITS, OTP_RANGE
from randomiser.pipeline.rejection_sampling import rejection_sample_int


def format_otp(value: int, *, digits: int = OTP_DIGITS) -> str:
    upper_bound = 10**digits
    if value < 0 or value >= upper_bound:
        raise ValueError(f"otp value must be in range [0, {upper_bound - 1}]")

    return f"{value:0{digits}d}"


def generate_otp_from_digest(digest: bytes, *, digits: int = OTP_DIGITS) -> str:
    upper_bound = 10**digits
    value = rejection_sample_int(digest, upper_bound=upper_bound)
    return format_otp(value, digits=digits)


def generate_six_digit_otp(digest: bytes) -> str:
    return generate_otp_from_digest(digest, digits=OTP_DIGITS)

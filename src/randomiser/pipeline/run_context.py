from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from randomiser.core.enums import RunMode
from randomiser.core.hashing import sha512_digest
from randomiser.io.artifact_namer import format_experiment_id, format_run_id


@dataclass(slots=True)
class RunContext:
    run_id: str
    mode: RunMode
    experiment_id: str
    created_at: datetime
    config_hash: str


def config_digest(config: dict[str, Any] | None = None) -> str:
    payload = json.dumps(config or {}, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha512_digest(payload).hex()


def build_run_context(
    run_number: int,
    *,
    mode: RunMode,
    experiment_id: str | None = None,
    config: dict[str, Any] | None = None,
    created_at: datetime | None = None,
) -> RunContext:
    timestamp = created_at or datetime.now(timezone.utc)
    return RunContext(
        run_id=format_run_id(run_number),
        mode=mode,
        experiment_id=experiment_id or format_experiment_id(timestamp),
        created_at=timestamp,
        config_hash=config_digest(config),
    )

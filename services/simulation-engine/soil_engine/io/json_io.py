from __future__ import annotations

import json
from pathlib import Path

from soil_engine.common.models import SimulationRequest, SimulationResult


def read_request(path: str | Path) -> SimulationRequest:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return SimulationRequest.model_validate(payload)


def write_result(path: str | Path, result: SimulationResult) -> None:
    Path(path).write_text(
        result.model_dump_json(by_alias=True, exclude_none=True, indent=2),
        encoding="utf-8",
    )

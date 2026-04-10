import json
from pathlib import Path

from soil_engine.common.models import SimulationRequest
from soil_engine.engine import run


def test_placeholder_engine_is_deterministic_for_same_input() -> None:
    fixture_path = (
        Path(__file__).resolve().parents[1] / "fixtures" / "sample_request.json"
    )
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    request = SimulationRequest.model_validate(payload)

    result_one = run(request)
    result_two = run(request)

    assert result_one.provenance.input_hash == result_two.provenance.input_hash
    assert result_one.provenance.result_hash == result_two.provenance.result_hash
    assert result_one.stable_payload() == result_two.stable_payload()

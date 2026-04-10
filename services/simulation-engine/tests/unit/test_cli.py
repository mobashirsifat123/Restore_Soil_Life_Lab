import json
from pathlib import Path

from soil_engine.cli import main


def test_cli_round_trip_writes_result_file(tmp_path: Path) -> None:
    fixture_path = (
        Path(__file__).resolve().parents[1] / "fixtures" / "sample_request.json"
    )
    output_path = tmp_path / "result.json"

    exit_code = main(["run", "--input", str(fixture_path), "--output", str(output_path)])

    assert exit_code == 0
    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["provenance"]["engineName"] == "soil-engine"
    assert payload["summary"]["nodeCount"] == 3
    assert payload["diagnostics"]["placeholder"] is True

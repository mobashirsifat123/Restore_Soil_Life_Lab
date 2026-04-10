from types import SimpleNamespace
from uuid import uuid4

from app.services.input_snapshot_builder import build_run_input_snapshot, compute_input_hash


def make_scenario_bundle():
    soil_sample_version_id = uuid4()
    return SimpleNamespace(
        id=uuid4(),
        stable_key=uuid4(),
        version=1,
        name="Baseline scenario",
        scenario_config_json={"horizonDays": 30},
        soil_sample_id=uuid4(),
        soil_sample_version_id=soil_sample_version_id,
        food_web_definition=SimpleNamespace(
            id=uuid4(),
            stable_key=uuid4(),
            version=1,
            nodes_json=[
                {
                    "key": "detritus",
                    "label": "Detritus",
                    "trophicGroup": "detritus",
                    "biomassCarbon": 100.0,
                    "biomassNitrogen": 12.0,
                    "isDetritus": True,
                    "metadata": {},
                }
            ],
            links_json=[],
            metadata_json={},
        ),
        soil_sample=SimpleNamespace(
            id=uuid4(),
            sample_code="SAMPLE-001",
        ),
        soil_sample_version=SimpleNamespace(
            id=soil_sample_version_id,
            version=3,
            sample_code="SAMPLE-001",
            measurements_json={"organicMatter": 4.2},
            location_json={"field": "North Plot"},
            metadata_json={},
        ),
        parameter_set=SimpleNamespace(
            id=uuid4(),
            stable_key=uuid4(),
            version=1,
            name="Baseline parameters",
            parameters_json={"respirationRate": 0.12},
            metadata_json={},
        ),
    )


def test_build_run_input_snapshot_contains_expected_reproducibility_fields():
    scenario = make_scenario_bundle()

    snapshot = build_run_input_snapshot(
        scenario=scenario,
        execution_options={"timeoutSeconds": 120, "requestedModules": ["flux", "stability"]},
        input_schema_version="1.0.0",
    )

    assert snapshot["inputSchemaVersion"] == "1.0.0"
    assert snapshot["foodWeb"]["version"] == 1
    assert snapshot["parameterSet"]["version"] == 1
    assert snapshot["scenario"]["version"] == 1
    assert snapshot["soilSample"]["version"] == 3
    assert "sampleVersionId" not in snapshot["soilSample"]
    assert snapshot["scenario"]["configuration"]["primarySoilSampleVersionId"] == str(
        scenario.soil_sample_version.id
    )
    assert snapshot["execution"]["deterministic"] is True
    assert snapshot["execution"]["requestedModules"] == ["flux", "stability"]


def test_compute_input_hash_ignores_operational_only_execution_fields():
    scenario = make_scenario_bundle()

    first_snapshot = build_run_input_snapshot(
        scenario=scenario,
        execution_options={"timeoutSeconds": 120, "metadata": {"requestId": "one"}},
        input_schema_version="1.0.0",
    )
    second_snapshot = build_run_input_snapshot(
        scenario=scenario,
        execution_options={"timeoutSeconds": 999, "metadata": {"requestId": "two"}},
        input_schema_version="1.0.0",
    )

    assert compute_input_hash(first_snapshot) == compute_input_hash(second_snapshot)

from __future__ import annotations

from typing import Any

from app.db.models import SimulationScenario
from app.schemas.scenario import extract_soil_sample_references, extract_user_scenario_config
from app.utils.hashing import sha256_for_value

DEFAULT_REQUESTED_MODULES = [
    "flux",
    "mineralization",
    "stability",
    "dynamics",
    "decomposition",
]
def _scientific_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = dict(snapshot)
    execution = dict(payload.get("execution", {}))
    execution.pop("runId", None)
    execution.pop("timeoutSeconds", None)
    execution.pop("metadata", None)
    payload["execution"] = execution
    return payload


def compute_input_hash(snapshot: dict[str, Any]) -> str:
    return sha256_for_value(_scientific_payload(snapshot))


def build_run_input_snapshot(
    *,
    scenario: SimulationScenario,
    execution_options: dict[str, Any],
    input_schema_version: str,
) -> dict[str, Any]:
    deterministic = bool(execution_options.get("deterministic", True))
    random_seed = int(execution_options.get("randomSeed", execution_options.get("random_seed", 0)))
    requested_modules = execution_options.get("requestedModules") or execution_options.get(
        "requested_modules",
        DEFAULT_REQUESTED_MODULES,
    )
    timeout_seconds = int(
        execution_options.get(
            "timeoutSeconds",
            execution_options.get("timeout_seconds", 120),
        )
    )
    primary_soil_sample_id = getattr(scenario, "soil_sample_id", scenario.soil_sample.id)
    scenario_configuration = extract_user_scenario_config(scenario.scenario_config_json)
    soil_sample_references = [
        reference.model_dump(mode="json", by_alias=True, exclude_none=True)
        for reference in extract_soil_sample_references(
            scenario.scenario_config_json,
            primary_soil_sample_id=primary_soil_sample_id,
            primary_soil_sample_version_id=scenario.soil_sample_version_id,
        )
    ]
    scenario_configuration["soilSampleReferences"] = soil_sample_references
    scenario_configuration["primarySoilSampleId"] = str(primary_soil_sample_id)
    scenario_configuration["primarySoilSampleVersionId"] = str(scenario.soil_sample_version_id)

    return {
        "inputSchemaVersion": input_schema_version,
        "foodWeb": {
            "definitionId": str(scenario.food_web_definition.id),
            "stableKey": str(scenario.food_web_definition.stable_key),
            "version": scenario.food_web_definition.version,
            "nodes": scenario.food_web_definition.nodes_json,
            "links": scenario.food_web_definition.links_json,
            "metadata": scenario.food_web_definition.metadata_json,
        },
        "soilSample": {
            "sampleId": str(scenario.soil_sample.id),
            "sampleCode": scenario.soil_sample_version.sample_code,
            "version": scenario.soil_sample_version.version,
            "measurements": scenario.soil_sample_version.measurements_json,
            "location": scenario.soil_sample_version.location_json,
            "metadata": scenario.soil_sample_version.metadata_json,
        },
        "parameterSet": {
            "parameterSetId": str(scenario.parameter_set.id),
            "stableKey": str(scenario.parameter_set.stable_key),
            "version": scenario.parameter_set.version,
            "name": scenario.parameter_set.name,
            "parameters": scenario.parameter_set.parameters_json,
            "metadata": scenario.parameter_set.metadata_json,
        },
        "scenario": {
            "scenarioId": str(scenario.id),
            "stableKey": str(scenario.stable_key),
            "version": scenario.version,
            "name": scenario.name,
            "configuration": scenario_configuration,
        },
        "execution": {
            "deterministic": deterministic,
            "randomSeed": random_seed,
            "requestedModules": requested_modules,
            "timeoutSeconds": timeout_seconds,
            "metadata": {},
        },
    }

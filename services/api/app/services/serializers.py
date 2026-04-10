from __future__ import annotations

from app.db.models import Project, RunArtifact, SimulationRun, SimulationScenario, SoilSample
from app.schemas.project import ProjectDetail
from app.schemas.run import RunArtifact as RunArtifactSchema
from app.schemas.run import RunDetail, RunResultsResponse, RunStatusResponse
from app.schemas.scenario import (
    ScenarioDetail,
    extract_soil_sample_references,
    extract_user_scenario_config,
)
from app.schemas.soil_sample import SoilSampleDetail


def _extract_snapshot_version(run: SimulationRun, *, section: str) -> int:
    snapshot = run.input_snapshot_json or {}
    section_payload = snapshot.get(section, {})
    value = section_payload.get("version", 1)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def serialize_project(project: Project) -> ProjectDetail:
    return ProjectDetail(
        id=project.id,
        organization_id=project.organization_id,
        name=project.name,
        slug=project.slug,
        description=project.description,
        status=project.status,
        metadata=project.metadata_json,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def serialize_soil_sample(soil_sample: SoilSample) -> SoilSampleDetail:
    return SoilSampleDetail(
        id=soil_sample.id,
        organization_id=soil_sample.organization_id,
        project_id=soil_sample.project_id,
        sample_code=soil_sample.sample_code,
        current_version_id=soil_sample.current_version_id,
        current_version=soil_sample.current_version,
        name=soil_sample.name,
        description=soil_sample.description,
        collected_on=soil_sample.collected_on,
        location=soil_sample.location_json,
        measurements=soil_sample.measurements_json,
        metadata=soil_sample.metadata_json,
        created_at=soil_sample.created_at,
        updated_at=soil_sample.updated_at,
    )


def serialize_scenario(scenario: SimulationScenario) -> ScenarioDetail:
    return ScenarioDetail(
        id=scenario.id,
        organization_id=scenario.organization_id,
        project_id=scenario.project_id,
        stable_key=scenario.stable_key,
        version=scenario.version,
        name=scenario.name,
        description=scenario.description,
        status=scenario.status,
        soil_sample_id=scenario.soil_sample_id,
        soil_sample_version_id=scenario.soil_sample_version_id,
        soil_sample_references=extract_soil_sample_references(
            scenario.scenario_config_json,
            primary_soil_sample_id=scenario.soil_sample_id,
            primary_soil_sample_version_id=scenario.soil_sample_version_id,
        ),
        food_web_definition_id=scenario.food_web_definition_id,
        parameter_set_id=scenario.parameter_set_id,
        scenario_config=extract_user_scenario_config(scenario.scenario_config_json),
        created_at=scenario.created_at,
        updated_at=scenario.updated_at,
    )


def serialize_run(run: SimulationRun) -> RunDetail:
    return RunDetail(
        id=run.id,
        organization_id=run.organization_id,
        project_id=run.project_id,
        scenario_id=run.scenario_id,
        status=run.status,
        engine_name=run.engine_name,
        engine_version=run.engine_version,
        input_schema_version=run.input_schema_version,
        parameter_set_version=_extract_snapshot_version(run, section="parameterSet"),
        soil_sample_version=_extract_snapshot_version(run, section="soilSample"),
        input_hash=run.input_hash,
        result_hash=run.result_hash,
        queued_at=run.queued_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        canceled_at=run.canceled_at,
        failure_code=run.failure_code,
        failure_message=run.failure_message,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


def serialize_run_status(run: SimulationRun) -> RunStatusResponse:
    return RunStatusResponse(
        id=run.id,
        status=run.status,
        queued_at=run.queued_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
        canceled_at=run.canceled_at,
        failure_code=run.failure_code,
        failure_message=run.failure_message,
    )


def serialize_artifact(artifact: RunArtifact) -> RunArtifactSchema:
    return RunArtifactSchema(
        id=artifact.id,
        artifact_type=artifact.artifact_type,
        label=artifact.label,
        content_type=artifact.content_type,
        storage_key=artifact.storage_key,
        byte_size=artifact.byte_size,
        checksum_sha256=artifact.checksum_sha256,
        metadata=artifact.metadata_json,
        created_at=artifact.created_at,
    )


def serialize_run_results(run: SimulationRun, artifacts: list[RunArtifact]) -> RunResultsResponse:
    return RunResultsResponse(
        id=run.id,
        status=run.status,
        engine_name=run.engine_name,
        engine_version=run.engine_version,
        parameter_set_version=_extract_snapshot_version(run, section="parameterSet"),
        soil_sample_version=_extract_snapshot_version(run, section="soilSample"),
        input_hash=run.input_hash,
        result_hash=run.result_hash,
        failure_code=run.failure_code,
        failure_message=run.failure_message,
        input_snapshot=run.input_snapshot_json,
        result_summary=run.result_summary_json,
        artifacts=[serialize_artifact(artifact) for artifact in artifacts],
    )

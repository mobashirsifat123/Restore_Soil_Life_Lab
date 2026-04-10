from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from soil_engine.common.enums import AnalysisModule
from soil_engine.common.hashing import sha256_for_value
from soil_engine.version import INPUT_SCHEMA_VERSION


def to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


class EngineModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,
        extra="forbid",
    )


class SpeciesNode(EngineModel):
    key: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=255)
    trophic_group: str = Field(min_length=1, max_length=100)
    biomass_carbon: float = Field(ge=0)
    biomass_nitrogen: float | None = Field(default=None, ge=0)
    is_detritus: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrophicLink(EngineModel):
    source: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=100)
    weight: float = Field(default=1.0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FoodWebInput(EngineModel):
    definition_id: UUID | None = None
    stable_key: UUID | None = None
    version: int = Field(default=1, ge=1)
    nodes: list[SpeciesNode] = Field(default_factory=list)
    links: list[TrophicLink] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_graph(self) -> "FoodWebInput":
        node_keys = [node.key for node in self.nodes]
        if len(node_keys) != len(set(node_keys)):
            raise ValueError("Food web node keys must be unique.")

        valid_keys = set(node_keys)
        for link in self.links:
            if link.source not in valid_keys or link.target not in valid_keys:
                raise ValueError("Every trophic link must reference known node keys.")
        return self


class SoilSampleInput(EngineModel):
    sample_id: UUID | None = None
    sample_code: str = Field(min_length=1, max_length=100)
    version: int = Field(default=1, ge=1)
    measurements: dict[str, Any] = Field(default_factory=dict)
    location: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ParameterSetInput(EngineModel):
    parameter_set_id: UUID | None = None
    stable_key: UUID | None = None
    version: int = Field(default=1, ge=1)
    name: str | None = Field(default=None, max_length=255)
    parameters: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScenarioInput(EngineModel):
    scenario_id: UUID | None = None
    stable_key: UUID | None = None
    version: int = Field(default=1, ge=1)
    name: str = Field(min_length=1, max_length=255)
    configuration: dict[str, Any] = Field(default_factory=dict)


class ExecutionOptions(EngineModel):
    run_id: UUID | None = None
    deterministic: bool = True
    random_seed: int = 0
    requested_modules: list[AnalysisModule] = Field(
        default_factory=lambda: [
            AnalysisModule.FLUX,
            AnalysisModule.MINERALIZATION,
            AnalysisModule.STABILITY,
            AnalysisModule.DYNAMICS,
            AnalysisModule.DECOMPOSITION,
        ]
    )
    timeout_seconds: int | None = Field(default=None, ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationRequest(EngineModel):
    input_schema_version: str = INPUT_SCHEMA_VERSION
    food_web: FoodWebInput
    soil_sample: SoilSampleInput
    parameter_set: ParameterSetInput
    scenario: ScenarioInput
    execution: ExecutionOptions = Field(default_factory=ExecutionOptions)

    def scientific_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        execution_payload = payload.get("execution", {})
        execution_payload.pop("runId", None)
        execution_payload.pop("timeoutSeconds", None)
        execution_payload.pop("metadata", None)
        return payload

    def scientific_input_hash(self) -> str:
        return sha256_for_value(self.scientific_payload())


class FluxResult(EngineModel):
    node_count: int
    link_count: int
    total_biomass_carbon: float
    total_biomass_nitrogen: float
    total_carbon_flux: float
    total_nitrogen_flux: float
    flux_matrix: list[list[float]] = Field(default_factory=list)


class MineralizationContribution(EngineModel):
    node_key: str
    direct_carbon: float
    indirect_carbon: float
    direct_nitrogen: float
    indirect_nitrogen: float


class MineralizationResult(EngineModel):
    total_carbon_mineralization: float
    total_nitrogen_mineralization: float
    contributions: list[MineralizationContribution] = Field(default_factory=list)


class StabilityResult(EngineModel):
    connectance: float
    smin: float
    dominant_eigenvalue: float
    stable: bool


class DynamicsPoint(EngineModel):
    time: float
    biomass_by_node: dict[str, float] = Field(default_factory=dict)


class DynamicsResult(EngineModel):
    horizon_days: int
    step_count: int
    points: list[DynamicsPoint] = Field(default_factory=list)


class DecompositionResult(EngineModel):
    initial_detritus_carbon: float
    remaining_detritus_carbon: float
    decomposition_constant: float
    simulated_days: int


class SimulationSummary(EngineModel):
    node_count: int
    link_count: int
    requested_modules: list[AnalysisModule] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ResultProvenance(EngineModel):
    engine_name: str
    engine_version: str
    input_schema_version: str
    parameter_set_version: int
    module_versions: dict[str, str] = Field(default_factory=dict)
    deterministic: bool = True
    random_seed: int = 0
    input_hash: str
    result_hash: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    placeholder: bool = True


class SimulationResult(EngineModel):
    provenance: ResultProvenance
    summary: SimulationSummary
    flux: FluxResult | None = None
    mineralization: MineralizationResult | None = None
    stability: StabilityResult | None = None
    dynamics: DynamicsResult | None = None
    decomposition: DecompositionResult | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)

    def stable_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json", by_alias=True, exclude_none=True)
        payload.get("provenance", {}).pop("generatedAt", None)
        return payload


from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.domain.enums import ScenarioStatus
from app.schemas.common import ApiModel, CursorPage, JsonDict, to_camel

SCENARIO_STORAGE_SOIL_SAMPLE_REFERENCES_KEY = "soilSampleReferences"
SCENARIO_STORAGE_PRIMARY_SOIL_SAMPLE_ID_KEY = "primarySoilSampleId"
SCENARIO_STORAGE_PRIMARY_SOIL_SAMPLE_VERSION_ID_KEY = "primarySoilSampleVersionId"


class FutureReadyScenarioModel(ApiModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
        extra="allow",
    )


class FoodWebNodeInput(ApiModel):
    key: str = Field(min_length=1, max_length=100)
    label: str = Field(min_length=1, max_length=255)
    trophic_group: str = Field(min_length=1, max_length=100)
    biomass_carbon: float = Field(ge=0)
    biomass_nitrogen: float | None = Field(default=None, ge=0)
    is_detritus: bool = False
    metadata: JsonDict = Field(default_factory=dict)


class FoodWebLinkInput(ApiModel):
    source: str = Field(min_length=1, max_length=100)
    target: str = Field(min_length=1, max_length=100)
    weight: float = Field(default=1.0, ge=0)
    metadata: JsonDict = Field(default_factory=dict)


class FoodWebDraft(ApiModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    nodes: list[FoodWebNodeInput] = Field(default_factory=list)
    links: list[FoodWebLinkInput] = Field(default_factory=list)
    metadata: JsonDict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_graph(self) -> FoodWebDraft:
        if not self.nodes:
            raise ValueError("A scenario food web must include at least one node.")

        node_keys = [node.key for node in self.nodes]
        if len(node_keys) != len(set(node_keys)):
            raise ValueError("Food web node keys must be unique.")

        valid_keys = set(node_keys)
        for link in self.links:
            if link.source not in valid_keys or link.target not in valid_keys:
                raise ValueError("Every trophic link must reference known node keys.")
        return self


class ParameterSetDraft(ApiModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    parameters: JsonDict = Field(default_factory=dict)
    metadata: JsonDict = Field(default_factory=dict)


class ScenarioSoilSampleReference(ApiModel):
    soil_sample_id: UUID
    soil_sample_version_id: UUID | None = None
    role: str | None = Field(default=None, min_length=1, max_length=100)
    weight: float | None = Field(default=None, gt=0)
    metadata: JsonDict = Field(default_factory=dict)

    @field_validator("role")
    @classmethod
    def normalize_role(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class ScenarioConfiguration(FutureReadyScenarioModel):
    parameterization: JsonDict = Field(default_factory=dict)
    execution_defaults: JsonDict = Field(default_factory=dict)
    run_labels: list[str] = Field(default_factory=list)
    metadata: JsonDict = Field(default_factory=dict)


def dump_scenario_configuration(configuration: ScenarioConfiguration | None) -> dict:
    if configuration is None:
        return {}
    return configuration.model_dump(mode="json", by_alias=True, exclude_none=True)


def _normalize_references(
    *,
    primary_soil_sample_id: UUID | None,
    soil_sample_references: list[ScenarioSoilSampleReference],
    required: bool,
) -> tuple[UUID | None, list[ScenarioSoilSampleReference]]:
    references = list(soil_sample_references)

    if primary_soil_sample_id is not None:
        matching_index = next(
            (
                index
                for index, reference in enumerate(references)
                if reference.soil_sample_id == primary_soil_sample_id
            ),
            None,
        )
        if matching_index is None:
            references.insert(
                0,
                ScenarioSoilSampleReference(
                    soil_sample_id=primary_soil_sample_id,
                    role="primary",
                ),
            )
        elif matching_index != 0:
            references.insert(0, references.pop(matching_index))

    if required and not references:
        raise ValueError("At least one soil sample reference is required.")

    if references:
        reference_ids = [reference.soil_sample_id for reference in references]
        if len(reference_ids) != len(set(reference_ids)):
            raise ValueError("Scenario soil sample references must be unique.")
        return references[0].soil_sample_id, references

    return None, []


def build_stored_scenario_config(
    *,
    scenario_config: ScenarioConfiguration | dict | None,
    soil_sample_references: list[ScenarioSoilSampleReference],
    primary_soil_sample_id: UUID,
    primary_soil_sample_version_id: UUID,
) -> dict:
    if isinstance(scenario_config, ScenarioConfiguration):
        payload = dump_scenario_configuration(scenario_config)
    else:
        payload = dict(scenario_config or {})

    payload[SCENARIO_STORAGE_SOIL_SAMPLE_REFERENCES_KEY] = [
        reference.model_dump(mode="json", by_alias=True, exclude_none=True)
        for reference in soil_sample_references
    ]
    payload[SCENARIO_STORAGE_PRIMARY_SOIL_SAMPLE_ID_KEY] = str(primary_soil_sample_id)
    payload[SCENARIO_STORAGE_PRIMARY_SOIL_SAMPLE_VERSION_ID_KEY] = str(
        primary_soil_sample_version_id
    )
    return payload


def extract_soil_sample_references(
    scenario_config: JsonDict,
    *,
    primary_soil_sample_id: UUID,
    primary_soil_sample_version_id: UUID,
) -> list[ScenarioSoilSampleReference]:
    raw_references = scenario_config.get(SCENARIO_STORAGE_SOIL_SAMPLE_REFERENCES_KEY, [])
    if isinstance(raw_references, list) and raw_references:
        return [
            ScenarioSoilSampleReference.model_validate(reference)
            for reference in raw_references
        ]
    return [
        ScenarioSoilSampleReference(
            soil_sample_id=primary_soil_sample_id,
            soil_sample_version_id=primary_soil_sample_version_id,
            role="primary",
        )
    ]


def extract_user_scenario_config(scenario_config: JsonDict) -> JsonDict:
    return {
        key: value
        for key, value in scenario_config.items()
        if key
        not in {
            SCENARIO_STORAGE_SOIL_SAMPLE_REFERENCES_KEY,
            SCENARIO_STORAGE_PRIMARY_SOIL_SAMPLE_ID_KEY,
            SCENARIO_STORAGE_PRIMARY_SOIL_SAMPLE_VERSION_ID_KEY,
        }
    }


class ScenarioCreate(ApiModel):
    name: str = Field(min_length=3, max_length=255)
    description: str | None = None
    soil_sample_id: UUID | None = None
    soil_sample_version_id: UUID | None = None
    soil_sample_references: list[ScenarioSoilSampleReference] = Field(default_factory=list)
    food_web: FoodWebDraft
    parameter_set: ParameterSetDraft
    scenario_config: ScenarioConfiguration = Field(default_factory=ScenarioConfiguration)

    @model_validator(mode="after")
    def normalize_soil_samples(self) -> ScenarioCreate:
        primary_soil_sample_id, references = _normalize_references(
            primary_soil_sample_id=self.soil_sample_id,
            soil_sample_references=self.soil_sample_references,
            required=True,
        )
        self.soil_sample_id = primary_soil_sample_id
        self.soil_sample_references = references
        return self


class ScenarioUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    status: ScenarioStatus | None = None
    soil_sample_id: UUID | None = None
    soil_sample_version_id: UUID | None = None
    soil_sample_references: list[ScenarioSoilSampleReference] | None = None
    food_web: FoodWebDraft | None = None
    parameter_set: ParameterSetDraft | None = None
    scenario_config: ScenarioConfiguration | None = None

    @model_validator(mode="after")
    def normalize_optional_soil_samples(self) -> ScenarioUpdate:
        if (
            "soil_sample_id" not in self.model_fields_set
            and "soil_sample_references" not in self.model_fields_set
        ):
            return self

        primary_soil_sample_id, references = _normalize_references(
            primary_soil_sample_id=self.soil_sample_id,
            soil_sample_references=self.soil_sample_references or [],
            required=True,
        )
        self.soil_sample_id = primary_soil_sample_id
        self.soil_sample_references = references
        return self


class ScenarioDetail(ApiModel):
    id: UUID
    organization_id: UUID
    project_id: UUID
    stable_key: UUID
    version: int
    name: str
    description: str | None = None
    status: ScenarioStatus
    soil_sample_id: UUID
    soil_sample_version_id: UUID
    soil_sample_references: list[ScenarioSoilSampleReference] = Field(default_factory=list)
    food_web_definition_id: UUID
    parameter_set_id: UUID
    scenario_config: JsonDict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class ScenarioListResponse(CursorPage):
    items: list[ScenarioDetail]

from __future__ import annotations

import re
from datetime import date, datetime
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.schemas.common import ApiModel, CursorPage, JsonDict, to_camel

SAMPLE_CODE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ScientificExpansionModel(ApiModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
        extra="allow",
    )


class SoilSampleLocation(ScientificExpansionModel):
    site_name: str | None = Field(default=None, max_length=255)
    field_name: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    elevation_m: float | None = None
    depth_cm: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_coordinates(self) -> SoilSampleLocation:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together.")
        return self


class SoilSampleMeasurements(ScientificExpansionModel):
    ph: float | None = Field(default=None, ge=0, le=14)
    moisture_percent: float | None = Field(default=None, ge=0, le=100)
    organic_matter_percent: float | None = Field(default=None, ge=0, le=100)
    nitrate_ppm: float | None = Field(default=None, ge=0)
    ammonium_ppm: float | None = Field(default=None, ge=0)
    bulk_density_g_cm3: float | None = Field(default=None, gt=0)
    temperature_c: float | None = None


def scientific_model_dump(model: ScientificExpansionModel | None) -> dict:
    if model is None:
        return {}
    return model.model_dump(mode="json", by_alias=True, exclude_none=True)


class SoilSampleCreate(ApiModel):
    sample_code: str = Field(min_length=1, max_length=100)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    collected_on: date | None = None
    location: SoilSampleLocation = Field(default_factory=SoilSampleLocation)
    measurements: SoilSampleMeasurements = Field(default_factory=SoilSampleMeasurements)
    metadata: JsonDict = Field(default_factory=dict)

    @field_validator("sample_code")
    @classmethod
    def validate_sample_code(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or not SAMPLE_CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "sample_code must start with an alphanumeric character and contain only letters, "
                "numbers, dots, underscores, or dashes."
            )
        return normalized

    @field_validator("name", "description")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("collected_on")
    @classmethod
    def validate_collected_on(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("collected_on cannot be in the future.")
        return value


class SoilSampleUpdate(ApiModel):
    sample_code: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    collected_on: date | None = None
    location: SoilSampleLocation | None = None
    measurements: SoilSampleMeasurements | None = None
    metadata: JsonDict | None = None

    @field_validator("sample_code")
    @classmethod
    def validate_optional_sample_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized or not SAMPLE_CODE_PATTERN.fullmatch(normalized):
            raise ValueError(
                "sample_code must start with an alphanumeric character and contain only letters, "
                "numbers, dots, underscores, or dashes."
            )
        return normalized

    @field_validator("name", "description")
    @classmethod
    def normalize_optional_update_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("collected_on")
    @classmethod
    def validate_update_collected_on(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("collected_on cannot be in the future.")
        return value


class SoilSampleDetail(ApiModel):
    id: UUID
    organization_id: UUID
    project_id: UUID
    sample_code: str
    current_version_id: UUID
    current_version: int
    name: str | None = None
    description: str | None = None
    collected_on: date | None = None
    location: JsonDict = Field(default_factory=dict)
    measurements: JsonDict = Field(default_factory=dict)
    metadata: JsonDict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class SoilSampleListResponse(CursorPage):
    items: list[SoilSampleDetail]

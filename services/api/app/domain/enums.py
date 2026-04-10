from __future__ import annotations

from enum import StrEnum


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ScenarioStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class RunStatus(StrEnum):
    DRAFT = "draft"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELED = "canceled"


class ArtifactType(StrEnum):
    RESULT_JSON = "result_json"
    SUMMARY_JSON = "summary_json"
    CSV_EXPORT = "csv_export"
    PLOT_IMAGE = "plot_image"
    REPORT_PDF = "report_pdf"
    LOG_BUNDLE = "log_bundle"
    OTHER = "other"

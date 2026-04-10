from app.domain.enums import RunStatus

ALLOWED_RUN_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    RunStatus.DRAFT: {RunStatus.QUEUED, RunStatus.CANCELED},
    RunStatus.QUEUED: {RunStatus.RUNNING, RunStatus.FAILED, RunStatus.CANCEL_REQUESTED, RunStatus.CANCELED},
    RunStatus.RUNNING: {
        RunStatus.SUCCEEDED,
        RunStatus.FAILED,
        RunStatus.CANCEL_REQUESTED,
        RunStatus.CANCELED,
    },
    RunStatus.CANCEL_REQUESTED: {RunStatus.CANCELED, RunStatus.FAILED},
    RunStatus.SUCCEEDED: set(),
    RunStatus.FAILED: set(),
    RunStatus.CANCELED: set(),
}

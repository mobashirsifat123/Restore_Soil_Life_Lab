from collections.abc import Callable

from app.jobs.handlers.decomposition_run import handle_decomposition_run
from app.jobs.handlers.report_generation import handle_report_generation
from app.jobs.handlers.simulation_run import handle_simulation_run
from app.jobs.payloads import JobType

Handler = Callable[..., None]

JOB_HANDLERS: dict[JobType, Handler] = {
    JobType.SIMULATION_RUN: handle_simulation_run,
    JobType.DECOMPOSITION_RUN: handle_decomposition_run,
    JobType.REPORT_GENERATION: handle_report_generation,
}


def get_handler(job_type: JobType) -> Handler:
    return JOB_HANDLERS[job_type]

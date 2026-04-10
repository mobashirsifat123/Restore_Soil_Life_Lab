from __future__ import annotations

from typing import Any

from soil_engine.common.enums import AnalysisModule
from soil_engine.common.errors import DeterminismError
from soil_engine.common.hashing import sha256_for_value
from soil_engine.common.models import (
    ResultProvenance,
    SimulationRequest,
    SimulationResult,
    SimulationSummary,
)
from soil_engine.decomposition.simulator import simulate_decomposition
from soil_engine.dynamics.simulator import simulate_dynamics
from soil_engine.flux.calculator import calculate_fluxes
from soil_engine.mineralization.analyzer import analyze_mineralization
from soil_engine.stability.analyzer import calculate_stability
from soil_engine.version import ENGINE_NAME, ENGINE_VERSION, MODULE_VERSIONS


def _validate_execution_mode(request: SimulationRequest) -> None:
    if not request.execution.deterministic:
        raise DeterminismError("The placeholder engine supports deterministic execution only.")


def run(request: SimulationRequest | dict[str, Any]) -> SimulationResult:
    simulation_request = (
        request if isinstance(request, SimulationRequest) else SimulationRequest.model_validate(request)
    )
    _validate_execution_mode(simulation_request)

    flux_result = None
    mineralization_result = None
    stability_result = None
    dynamics_result = None
    decomposition_result = None

    requested_modules = set(simulation_request.execution.requested_modules)
    if AnalysisModule.FLUX in requested_modules:
        flux_result = calculate_fluxes(simulation_request)
    if AnalysisModule.MINERALIZATION in requested_modules:
        mineralization_result = analyze_mineralization(simulation_request, flux_result)
    if AnalysisModule.STABILITY in requested_modules:
        stability_result = calculate_stability(simulation_request)
    if AnalysisModule.DYNAMICS in requested_modules:
        dynamics_result = simulate_dynamics(simulation_request)
    if AnalysisModule.DECOMPOSITION in requested_modules:
        decomposition_result = simulate_decomposition(simulation_request)

    warnings: list[str] = []
    if flux_result is None and mineralization_result is not None:
        warnings.append("Mineralization was requested without flux output; zero flux fallback applied.")

    summary = SimulationSummary(
        node_count=len(simulation_request.food_web.nodes),
        link_count=len(simulation_request.food_web.links),
        requested_modules=list(simulation_request.execution.requested_modules),
        warnings=warnings,
    )

    input_hash = simulation_request.scientific_input_hash()
    result_payload = {
        "summary": summary.model_dump(mode="json", by_alias=True, exclude_none=True),
        "flux": None if flux_result is None else flux_result.model_dump(mode="json", by_alias=True),
        "mineralization": (
            None
            if mineralization_result is None
            else mineralization_result.model_dump(mode="json", by_alias=True)
        ),
        "stability": (
            None if stability_result is None else stability_result.model_dump(mode="json", by_alias=True)
        ),
        "dynamics": (
            None if dynamics_result is None else dynamics_result.model_dump(mode="json", by_alias=True)
        ),
        "decomposition": (
            None
            if decomposition_result is None
            else decomposition_result.model_dump(mode="json", by_alias=True)
        ),
        "diagnostics": {
            "placeholder": True,
            "engineName": ENGINE_NAME,
            "engineVersion": ENGINE_VERSION,
            "requestedModules": [str(module) for module in simulation_request.execution.requested_modules],
            "moduleVersions": MODULE_VERSIONS,
        },
    }
    result_hash = sha256_for_value(result_payload)

    provenance = ResultProvenance(
        engine_name=ENGINE_NAME,
        engine_version=ENGINE_VERSION,
        input_schema_version=simulation_request.input_schema_version,
        parameter_set_version=simulation_request.parameter_set.version,
        module_versions=MODULE_VERSIONS,
        deterministic=simulation_request.execution.deterministic,
        random_seed=simulation_request.execution.random_seed,
        input_hash=input_hash,
        result_hash=result_hash,
        placeholder=True,
    )

    return SimulationResult(
        provenance=provenance,
        summary=summary,
        flux=flux_result,
        mineralization=mineralization_result,
        stability=stability_result,
        dynamics=dynamics_result,
        decomposition=decomposition_result,
        diagnostics=result_payload["diagnostics"],
    )

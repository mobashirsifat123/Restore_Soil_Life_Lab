from __future__ import annotations

from soil_engine.common.models import SimulationRequest, StabilityResult


def calculate_stability(request: SimulationRequest) -> StabilityResult:
    node_count = len(request.food_web.nodes)
    link_count = len(request.food_web.links)
    total_carbon = sum(node.biomass_carbon for node in request.food_web.nodes)

    possible_links = max(node_count * node_count, 1)
    connectance = round(link_count / possible_links, 6)
    smin = round((total_carbon / max(node_count, 1)) * 0.05, 6)
    dominant_eigenvalue = round(connectance - 0.5, 6)
    stable = dominant_eigenvalue < 0

    return StabilityResult(
        connectance=connectance,
        smin=smin,
        dominant_eigenvalue=dominant_eigenvalue,
        stable=stable,
    )

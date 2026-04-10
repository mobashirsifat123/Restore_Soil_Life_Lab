from __future__ import annotations

from soil_engine.common.models import FluxResult, SimulationRequest


def calculate_fluxes(request: SimulationRequest) -> FluxResult:
    node_count = len(request.food_web.nodes)
    link_count = len(request.food_web.links)
    total_carbon = sum(node.biomass_carbon for node in request.food_web.nodes)
    total_nitrogen = sum(node.biomass_nitrogen or 0.0 for node in request.food_web.nodes)

    node_index = {node.key: index for index, node in enumerate(request.food_web.nodes)}
    flux_matrix = [[0.0 for _ in range(node_count)] for _ in range(node_count)]

    for link in request.food_web.links:
        source_index = node_index[link.source]
        target_index = node_index[link.target]
        source_node = request.food_web.nodes[source_index]
        flux_matrix[source_index][target_index] = round(source_node.biomass_carbon * link.weight * 0.01, 6)

    total_carbon_flux = round(sum(sum(row) for row in flux_matrix), 6)
    nitrogen_factor = link_count / max(node_count, 1)
    total_nitrogen_flux = round(total_nitrogen * nitrogen_factor * 0.01, 6)

    return FluxResult(
        node_count=node_count,
        link_count=link_count,
        total_biomass_carbon=round(total_carbon, 6),
        total_biomass_nitrogen=round(total_nitrogen, 6),
        total_carbon_flux=total_carbon_flux,
        total_nitrogen_flux=total_nitrogen_flux,
        flux_matrix=flux_matrix,
    )

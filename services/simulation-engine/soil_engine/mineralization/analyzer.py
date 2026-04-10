from __future__ import annotations

from soil_engine.common.models import (
    FluxResult,
    MineralizationContribution,
    MineralizationResult,
    SimulationRequest,
)


def analyze_mineralization(
    request: SimulationRequest,
    flux_result: FluxResult | None,
) -> MineralizationResult:
    total_carbon = sum(node.biomass_carbon for node in request.food_web.nodes)
    total_nitrogen = sum(node.biomass_nitrogen or 0.0 for node in request.food_web.nodes)
    carbon_flux = flux_result.total_carbon_flux if flux_result else 0.0
    nitrogen_flux = flux_result.total_nitrogen_flux if flux_result else 0.0

    contributions: list[MineralizationContribution] = []
    for node in request.food_web.nodes:
        carbon_share = 0.0 if total_carbon == 0 else node.biomass_carbon / total_carbon
        nitrogen_share = 0.0 if total_nitrogen == 0 else (node.biomass_nitrogen or 0.0) / total_nitrogen
        contributions.append(
            MineralizationContribution(
                node_key=node.key,
                direct_carbon=round(carbon_flux * carbon_share * 0.6, 6),
                indirect_carbon=round(carbon_flux * carbon_share * 0.4, 6),
                direct_nitrogen=round(nitrogen_flux * nitrogen_share * 0.55, 6),
                indirect_nitrogen=round(nitrogen_flux * nitrogen_share * 0.45, 6),
            )
        )

    return MineralizationResult(
        total_carbon_mineralization=round(carbon_flux, 6),
        total_nitrogen_mineralization=round(nitrogen_flux, 6),
        contributions=contributions,
    )

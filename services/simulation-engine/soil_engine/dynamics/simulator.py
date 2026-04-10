from __future__ import annotations

import math

from soil_engine.common.models import DynamicsPoint, DynamicsResult, SimulationRequest


def simulate_dynamics(request: SimulationRequest) -> DynamicsResult:
    horizon_days = int(request.scenario.configuration.get("timeHorizonDays", 30))
    step_count = int(request.scenario.configuration.get("timeSteps", 5))
    step_count = max(step_count, 2)
    decay_factor = float(request.parameter_set.parameters.get("dynamic_decay_factor", 0.015))

    points: list[DynamicsPoint] = []
    for step in range(step_count):
        time = round((horizon_days / (step_count - 1)) * step, 6)
        biomass_by_node = {}
        for node in request.food_web.nodes:
            biomass = node.biomass_carbon * math.exp(-decay_factor * time)
            biomass_by_node[node.key] = round(biomass, 6)
        points.append(DynamicsPoint(time=time, biomass_by_node=biomass_by_node))

    return DynamicsResult(horizon_days=horizon_days, step_count=step_count, points=points)

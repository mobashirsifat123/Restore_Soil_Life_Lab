from __future__ import annotations

import math

from simpleeval import simple_eval

from soil_engine.common.models import DecompositionResult, SimulationRequest


def simulate_decomposition(request: SimulationRequest) -> DecompositionResult:
    simulated_days = int(request.scenario.configuration.get("decompositionDays", 30))
    detritus_nodes = [node for node in request.food_web.nodes if node.is_detritus]
    initial_detritus = sum(node.biomass_carbon for node in detritus_nodes)
    if initial_detritus == 0:
        initial_detritus = float(request.parameter_set.parameters.get("initial_detritus_carbon", 1.0))

    decomposition_constant = float(
        request.parameter_set.parameters.get(
            "decomposition_constant",
            round(0.01 + len(request.food_web.links) * 0.001, 6),
        )
    )
    
    remaining_detritus = round(initial_detritus * math.exp(-decomposition_constant * simulated_days), 6)

    # Dynamic formula override
    equations = request.scenario.configuration.get("equations", [])
    for eq in equations:
        if eq.get("key") == "decomposition_constant":
            try:
                decomposition_constant = float(simple_eval(
                    eq["expression"],
                    names={
                        "initial_detritus": initial_detritus,
                        "simulated_days": simulated_days,
                        "link_count": len(request.food_web.links),
                        "node_count": len(request.food_web.nodes)
                    }
                ))
            except Exception:
                pass
        elif eq.get("key") == "remaining_detritus":
            try:
                remaining_detritus = float(simple_eval(
                    eq["expression"],
                    names={
                        "initial_detritus": initial_detritus,
                        "decomposition_constant": decomposition_constant,
                        "simulated_days": simulated_days,
                        "exp": math.exp
                    }
                ))
            except Exception:
                pass

    return DecompositionResult(
        initial_detritus_carbon=round(initial_detritus, 6),
        remaining_detritus_carbon=round(remaining_detritus, 6),
        decomposition_constant=round(decomposition_constant, 6),
        simulated_days=simulated_days,
    )

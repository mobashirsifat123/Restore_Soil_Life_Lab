from uuid import uuid4

import pytest

from soil_engine.common.errors import DeterminismError
from soil_engine.common.models import (
    ExecutionOptions,
    FoodWebInput,
    ParameterSetInput,
    ScenarioInput,
    SimulationRequest,
    SoilSampleInput,
    SpeciesNode,
    TrophicLink,
)
from soil_engine.engine import run


def build_base_request() -> SimulationRequest:
    return SimulationRequest(
        food_web=FoodWebInput(
            definition_id=uuid4(),
            nodes=[
                SpeciesNode(
                    key="detritus",
                    label="Detritus",
                    trophic_group="detritus",
                    biomass_carbon=10.0,
                    is_detritus=True,
                ),
                SpeciesNode(
                    key="fungi",
                    label="Fungi",
                    trophic_group="fungus",
                    biomass_carbon=5.0,
                ),
            ],
            links=[TrophicLink(source="detritus", target="fungi", weight=0.5)],
        ),
        soil_sample=SoilSampleInput(
            sample_id=uuid4(),
            sample_code="S-VALIDATION-1",
            measurements={"ph": 6.8},
        ),
        parameter_set=ParameterSetInput(
            parameter_set_id=uuid4(),
            parameters={"dynamic_decay_factor": 0.02},
        ),
        scenario=ScenarioInput(
            scenario_id=uuid4(),
            name="Validation Scenario",
            configuration={"timeHorizonDays": 10, "timeSteps": 3},
        ),
    )


def test_food_web_rejects_duplicate_node_keys() -> None:
    with pytest.raises(ValueError, match="must be unique"):
        FoodWebInput(
            definition_id=uuid4(),
            nodes=[
                SpeciesNode(
                    key="fungi",
                    label="Fungi A",
                    trophic_group="fungus",
                    biomass_carbon=4.0,
                ),
                SpeciesNode(
                    key="fungi",
                    label="Fungi B",
                    trophic_group="fungus",
                    biomass_carbon=6.0,
                ),
            ],
            links=[],
        )


def test_placeholder_engine_rejects_non_deterministic_execution() -> None:
    request = build_base_request().model_copy(
        update=(
            {
                "execution": ExecutionOptions(
                    deterministic=False,
                    random_seed=42,
                )
            }
        )
    )

    with pytest.raises(DeterminismError, match="deterministic execution only"):
        run(request)

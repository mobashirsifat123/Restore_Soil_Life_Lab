from uuid import uuid4

from soil_engine.common.enums import AnalysisModule
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


def build_request() -> SimulationRequest:
    return SimulationRequest(
        food_web=FoodWebInput(
            definition_id=uuid4(),
            version=1,
            nodes=[
                SpeciesNode(
                    key="detritus",
                    label="Detritus",
                    trophic_group="detritus",
                    biomass_carbon=12.0,
                    biomass_nitrogen=2.5,
                    is_detritus=True,
                ),
                SpeciesNode(
                    key="bacteria",
                    label="Bacteria",
                    trophic_group="microbe",
                    biomass_carbon=4.0,
                    biomass_nitrogen=1.0,
                ),
            ],
            links=[TrophicLink(source="detritus", target="bacteria", weight=0.8)],
        ),
        soil_sample=SoilSampleInput(
            sample_id=uuid4(),
            sample_code="S-001",
            measurements={"ph": 6.4, "moisture": 0.32},
        ),
        parameter_set=ParameterSetInput(
            parameter_set_id=uuid4(),
            version=2,
            parameters={"dynamic_decay_factor": 0.02, "decomposition_constant": 0.03},
        ),
        scenario=ScenarioInput(
            scenario_id=uuid4(),
            version=1,
            name="Baseline",
            configuration={"timeHorizonDays": 20, "timeSteps": 4, "decompositionDays": 14},
        ),
        execution=ExecutionOptions(
            requested_modules=[
                AnalysisModule.FLUX,
                AnalysisModule.MINERALIZATION,
                AnalysisModule.STABILITY,
                AnalysisModule.DYNAMICS,
                AnalysisModule.DECOMPOSITION,
            ]
        ),
    )


def test_run_returns_all_placeholder_modules() -> None:
    request = build_request()

    result = run(request)

    assert result.flux is not None
    assert result.mineralization is not None
    assert result.stability is not None
    assert result.dynamics is not None
    assert result.decomposition is not None
    assert result.provenance.engine_name == "soil-engine"
    assert result.provenance.input_hash
    assert result.provenance.result_hash
    assert result.summary.node_count == 2

from enum import StrEnum


class AnalysisModule(StrEnum):
    FLUX = "flux"
    MINERALIZATION = "mineralization"
    STABILITY = "stability"
    DYNAMICS = "dynamics"
    DECOMPOSITION = "decomposition"

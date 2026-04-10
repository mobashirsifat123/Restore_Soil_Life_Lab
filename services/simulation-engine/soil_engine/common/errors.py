from __future__ import annotations


class SoilEngineError(Exception):
    """Base error for scientific engine failures."""


class DeterminismError(SoilEngineError):
    """Raised when a request violates deterministic execution rules."""


class UnsupportedModuleError(SoilEngineError):
    """Raised when the request references an unsupported analysis module."""

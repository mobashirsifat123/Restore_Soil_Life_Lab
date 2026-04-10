# Simulation Engine Architecture

## Purpose

This document defines the package boundary and architecture for the Python-based scientific engine used by the Bio Soil platform.

It is optimized for:

- independence from FastAPI, SQLAlchemy, Redis, and HTTP concerns
- deterministic and reproducible outputs
- modular scientific development
- testability and benchmarking
- safe invocation from a worker process

## Boundary Rules

The simulation engine may depend on:

- Python standard library
- scientific libraries such as `numpy`, `scipy`, `pandas`, and `networkx`
- validation and serialization libraries such as `pydantic`

The simulation engine must not depend on:

- FastAPI
- Starlette
- SQLAlchemy
- Alembic
- Redis clients
- object storage SDKs
- request or response objects
- environment-managed application state

The engine accepts structured scientific inputs and returns structured scientific outputs. It should not know where those inputs came from or where results are stored.

## Directory Tree

```text
services/simulation-engine/
├── pyproject.toml
├── README.md
├── soil_engine/
│   ├── __init__.py
│   ├── cli.py
│   ├── engine.py
│   ├── version.py
│   ├── common/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── errors.py
│   │   ├── hashing.py
│   │   └── models.py
│   ├── flux/
│   │   ├── __init__.py
│   │   └── calculator.py
│   ├── mineralization/
│   │   ├── __init__.py
│   │   └── analyzer.py
│   ├── stability/
│   │   ├── __init__.py
│   │   └── analyzer.py
│   ├── dynamics/
│   │   ├── __init__.py
│   │   └── simulator.py
│   ├── decomposition/
│   │   ├── __init__.py
│   │   └── simulator.py
│   └── io/
│       ├── __init__.py
│       └── json_io.py
└── tests/
    ├── unit/
    ├── regression/
    ├── fixtures/
    └── benchmarks/
```

## Core Abstractions

### `SimulationRequest`

The full scientific input contract.

Contains:

- `food_web`
- `soil_sample`
- `parameter_set`
- `scenario`
- `execution`
- `input_schema_version`

Important:

This request is the canonical input that should be stored in `simulation_runs.input_snapshot_json`.

### `SimulationResult`

The full scientific output contract.

Contains:

- `provenance`
- `summary`
- optional outputs for flux, mineralization, stability, dynamics, and decomposition
- `diagnostics`

### `ResultProvenance`

The reproducibility payload for every result.

Contains:

- `engine_name`
- `engine_version`
- `input_schema_version`
- `parameter_set_version`
- `module_versions`
- `deterministic`
- `random_seed`
- `input_hash`
- `result_hash`
- `generated_at`
- `placeholder`

### Module Contracts

Each scientific area has one public function:

- `calculate_fluxes(request)`
- `analyze_mineralization(request, flux_result)`
- `calculate_stability(request)`
- `simulate_dynamics(request)`
- `simulate_decomposition(request)`

These functions must:

- accept pure models
- return pure models
- avoid IO
- avoid global mutable state

## Input Schema

The current engine uses Pydantic models in:

- [models.py](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/soil_engine/common/models.py)

Main components:

- `SpeciesNode`
- `TrophicLink`
- `FoodWebInput`
- `SoilSampleInput`
- `ParameterSetInput`
- `ScenarioInput`
- `ExecutionOptions`
- `SimulationRequest`

Important design rule:

The engine computes the scientific input hash from `SimulationRequest.scientific_payload()`, which excludes operational-only fields such as `runId`, timeout values, and miscellaneous metadata.

## Output Schema

Current outputs include:

- `FluxResult`
- `MineralizationResult`
- `StabilityResult`
- `DynamicsResult`
- `DecompositionResult`
- `SimulationSummary`
- `ResultProvenance`
- `SimulationResult`

The output shape is explicit and versioned, which makes it safe for:

- artifact serialization
- regression testing
- worker subprocess invocation

## `run()` Entrypoint

Current entrypoint:

- [engine.py](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/soil_engine/engine.py)

Behavior:

1. validate the request
2. execute the requested scientific modules in a deterministic order
3. build a summary
4. compute `input_hash`
5. compute `result_hash`
6. attach provenance
7. return `SimulationResult`

This function is the stable in-process API the worker can call if it already owns execution isolation.

## CLI Entrypoint

Current CLI:

- [cli.py](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/soil_engine/cli.py)

Recommended worker invocation:

```bash
python -m soil_engine.cli run --input /tmp/request.json --output /tmp/result.json
```

Why this is a good boundary:

- the worker can execute the engine in a subprocess
- timeouts and cancellation are easier to enforce
- stdout and stderr can be captured separately from structured result JSON
- the engine package remains unaware of Redis and PostgreSQL

## Placeholder Calculation Flow

Current placeholder execution order:

1. flux calculation
2. mineralization analysis using flux output
3. stability calculation
4. non-equilibrium dynamics simulation
5. decomposition simulation

The placeholder logic is intentionally simple and deterministic:

- flux is derived from node biomass and link weights
- mineralization is apportioned by biomass share
- stability uses connectance and a simple `smin` heuristic
- dynamics uses exponential decay over a fixed horizon
- decomposition uses deterministic decay from detritus biomass

These are scaffolds only. They are not the final scientific models.

## Versioning Strategy

Track three version dimensions:

### 1. Engine Code Version

Defined in:

- [version.py](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/soil_engine/version.py)

Use semantic versioning:

- major: breaking changes to scientific behavior or output compatibility
- minor: additive features or new supported modules
- patch: bug fixes that do not intentionally change scientific meaning

### 2. Input Schema Version

Also defined in `version.py`.

Bump this when the request contract changes in a way that affects serialization or validation.

### 3. Parameter Set Version

Comes from the platform database and is included in `ParameterSetInput.version`.

Rules:

- parameter set versions are owned by the platform domain model
- engine provenance must always echo the parameter set version used
- runs should never rely on mutable live parameter rows; use the snapshot

### Optional Future Extension

The engine already exposes `MODULE_VERSIONS`. Keep that map once modules evolve independently.

## Deterministic Run Rules

1. Compute hashes from canonical JSON serialization with sorted keys.
2. Exclude operational-only fields from the scientific input hash.
3. Avoid global mutable state.
4. Do not read environment variables inside scientific calculations.
5. If randomness is introduced later, require an explicit seed and include it in provenance.
6. Do not depend on wall-clock time except for provenance timestamps.
7. Compute `result_hash` from scientific outputs, not transient metadata like `generated_at`.
8. Use fixed numeric precision at API boundaries where appropriate.

## What Goes In The Database vs Artifact Files

### Store In Database

In `simulation_runs`:

- `input_snapshot_json`
- `input_hash`
- `engine_name`
- `engine_version`
- `input_schema_version`
- `result_summary_json`
- `result_hash`
- lifecycle metadata and failure metadata

The DB should contain enough information to list, filter, and audit runs quickly.

### Store As Artifact Files

Store as object-storage artifacts:

- full raw result JSON
- dense matrices
- long time series
- plots
- diagnostic bundles
- benchmark or trace payloads if needed

Rule:

The database stores queryable summary and provenance. Artifact files store large or bulky scientific outputs.

## Worker Integration

The worker should:

1. load the authoritative `input_snapshot_json` from the run row
2. write that snapshot to a temporary JSON file
3. invoke `python -m soil_engine.cli run --input ... --output ...`
4. read the result JSON
5. upload the full result as an artifact
6. persist summary and provenance fields to the run row

This keeps the engine independent while still allowing hard subprocess timeouts and isolation.

## Testing Strategy

### Unit Tests

Test individual module functions and input validation:

- [test_engine.py](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/tests/unit/test_engine.py)

### Regression Tests

Use fixed JSON fixtures and compare stable outputs:

- [test_determinism.py](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/tests/regression/test_determinism.py)
- [sample_request.json](/Users/mobashirsifat/Desktop/bio_lab/services/simulation-engine/tests/fixtures/sample_request.json)

### Benchmark Tests

Reserve `tests/benchmarks` for:

- small graph
- medium graph
- large graph
- long-horizon dynamics

### Promotion Rule

No scientific algorithm should replace a placeholder implementation until:

- it has fixture-based regression tests
- it has at least one benchmark case
- its version impact is documented

## MVP Placeholder Implementation Rules

For MVP:

- keep module interfaces stable
- keep outputs deterministic
- keep formulas simple and explicit
- mark provenance as `placeholder=true`

This lets the platform prove end-to-end orchestration before final scientific methods are fully implemented.

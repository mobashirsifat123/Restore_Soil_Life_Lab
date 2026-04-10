# Soil Engine

`soil_engine` is the pure scientific computation package for the Bio Soil platform.

Design goals:

- no FastAPI, HTTP, SQLAlchemy, Redis, or object storage dependencies
- deterministic and reproducible results for the same scientific input snapshot
- versioned input schema and engine version
- testable at the module level and benchmarkable at the package level
- callable by a worker process through a stable Python API or subprocess CLI

Primary entrypoints:

- `soil_engine.run(request)` for in-process execution
- `python -m soil_engine.cli run --input input.json --output output.json` for subprocess execution

Architecture details live in [simulation-engine-architecture.md](/Users/mobashirsifat/Desktop/bio_lab/docs/domain/simulation-engine-architecture.md).

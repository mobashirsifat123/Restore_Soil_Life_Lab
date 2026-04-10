from __future__ import annotations

import argparse
from pathlib import Path

from soil_engine.engine import run
from soil_engine.io.json_io import read_request, write_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run soil engine simulations from JSON snapshots.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Execute a simulation request.")
    run_parser.add_argument("--input", required=True, help="Path to the simulation request JSON file.")
    run_parser.add_argument("--output", required=True, help="Path to the result JSON file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        request = read_request(Path(args.input))
        result = run(request)
        write_result(Path(args.output), result)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

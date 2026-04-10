from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
from pathlib import Path


class ExecutionService:
    """
    Executes untrusted or long-running work in an isolated subprocess.

    This service should:
    - spawn a fresh child process per scientific run or report render
    - enforce hard timeouts
    - kill the subprocess on timeout or cancellation
    - collect stdout/stderr for diagnostic artifacts
    - return only structured results to the parent worker

    Running the simulation engine directly in the long-lived worker process is discouraged because
    scientific libraries can leak memory, ignore cancellation, or crash the interpreter.
    """

    def __init__(
        self,
        *,
        worker_id: str,
        simulation_engine_command: str,
        simulation_engine_pythonpath: str,
        repository_root: Path | None = None,
    ) -> None:
        self.worker_id = worker_id
        self.simulation_engine_command = simulation_engine_command
        self.repository_root = repository_root or Path(__file__).resolve().parents[4]
        pythonpath = Path(simulation_engine_pythonpath)
        if not pythonpath.is_absolute():
            pythonpath = self.repository_root / pythonpath
        self.simulation_engine_pythonpath = str(pythonpath.resolve())

    def execute_simulation(self, *, run_id, input_snapshot: dict, timeout_seconds: int) -> dict:
        with tempfile.TemporaryDirectory(prefix=f"run-{run_id}-") as temp_dir:
            working_directory = Path(temp_dir)
            input_path = working_directory / "input.json"
            output_path = working_directory / "output.json"
            input_path.write_text(
                json.dumps(input_snapshot, ensure_ascii=True, indent=2, sort_keys=True),
                encoding="utf-8",
            )

            command = self.build_simulation_command(input_path=input_path, output_path=output_path)
            env = self.build_subprocess_environment()

            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                cwd=working_directory,
                env=env,
                text=True,
                timeout=timeout_seconds,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "Simulation execution failed: "
                    f"{completed.stderr.strip() or completed.stdout.strip() or 'unknown error'}"
                )
            if not output_path.exists():
                raise RuntimeError("Simulation engine finished without producing an output artifact.")

            result_payload = json.loads(output_path.read_text(encoding="utf-8"))
            return {
                "result": result_payload,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }

    def build_simulation_command(self, *, input_path: Path, output_path: Path) -> list[str]:
        return shlex.split(self.simulation_engine_command) + [
            "run",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ]

    def build_subprocess_environment(self) -> dict[str, str]:
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        path_parts = [self.simulation_engine_pythonpath]
        if existing_pythonpath:
            path_parts.append(existing_pythonpath)
        env["PYTHONPATH"] = os.pathsep.join(path_parts)
        return env

    def execute_report(self, *, report_id, input_snapshot: dict, timeout_seconds: int) -> dict:
        raise NotImplementedError("Execute report rendering in a subprocess and return artifact metadata.")

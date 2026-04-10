from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class StoredArtifact:
    artifact_type: str
    label: str
    content_type: str
    storage_key: str
    byte_size: int
    checksum_sha256: str
    metadata: dict[str, Any]


class ArtifactService:
    """
    Artifact write contract.

    Safe-write rules:
    - object keys must be deterministic by business id, not queue message id
    - upload must complete successfully before the DB metadata row is committed
    - checksum and byte size must be persisted with the artifact row
    - retries should overwrite identical content safely or no-op via checksum comparison
    """

    def __init__(self, *, bucket: str, root_path: str) -> None:
        self.bucket = bucket
        base_path = Path(root_path)
        if not base_path.is_absolute():
            repository_root = Path(__file__).resolve().parents[4]
            base_path = repository_root / base_path
        self.root_path = base_path.resolve()

    def build_run_artifact_key(self, *, run_id, artifact_name: str) -> str:
        return f"runs/{run_id}/{artifact_name}"

    def build_report_artifact_key(self, *, report_id, artifact_name: str) -> str:
        return f"reports/{report_id}/{artifact_name}"

    def write_json_artifact(self, *, key: str, payload: dict) -> dict:
        data = json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True).encode("utf-8")
        return self._write_bytes(key=key, data=data, content_type="application/json")

    def write_text_artifact(self, *, key: str, text_payload: str, content_type: str = "text/plain") -> dict:
        return self._write_bytes(key=key, data=text_payload.encode("utf-8"), content_type=content_type)

    def write_run_artifacts(
        self,
        *,
        run_id,
        result_payload: dict[str, Any],
        stdout: str,
        stderr: str,
    ) -> list[StoredArtifact]:
        artifacts: list[StoredArtifact] = []

        result_key = self.build_run_artifact_key(run_id=run_id, artifact_name="result.json")
        result_metadata = self.write_json_artifact(key=result_key, payload=result_payload)
        artifacts.append(
            StoredArtifact(
                artifact_type="result_json",
                label="Simulation result JSON",
                content_type=result_metadata["content_type"],
                storage_key=result_key,
                byte_size=result_metadata["byte_size"],
                checksum_sha256=result_metadata["checksum_sha256"],
                metadata={},
            )
        )

        summary_key = self.build_run_artifact_key(run_id=run_id, artifact_name="summary.json")
        summary_metadata = self.write_json_artifact(
            key=summary_key,
            payload={
                "summary": result_payload.get("summary"),
                "provenance": result_payload.get("provenance"),
            },
        )
        artifacts.append(
            StoredArtifact(
                artifact_type="summary_json",
                label="Simulation summary JSON",
                content_type=summary_metadata["content_type"],
                storage_key=summary_key,
                byte_size=summary_metadata["byte_size"],
                checksum_sha256=summary_metadata["checksum_sha256"],
                metadata={},
            )
        )

        log_key = self.build_run_artifact_key(run_id=run_id, artifact_name="diagnostics.log")
        log_metadata = self.write_text_artifact(
            key=log_key,
            text_payload=f"[stdout]\n{stdout}\n\n[stderr]\n{stderr}\n",
        )
        artifacts.append(
            StoredArtifact(
                artifact_type="log_bundle",
                label="Simulation diagnostics log",
                content_type=log_metadata["content_type"],
                storage_key=log_key,
                byte_size=log_metadata["byte_size"],
                checksum_sha256=log_metadata["checksum_sha256"],
                metadata={},
            )
        )

        return artifacts

    def _write_bytes(self, *, key: str, data: bytes, content_type: str) -> dict[str, Any]:
        destination = self.root_path / self.bucket / key
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return {
            "byte_size": len(data),
            "checksum_sha256": hashlib.sha256(data).hexdigest(),
            "content_type": content_type,
            "path": str(destination),
        }

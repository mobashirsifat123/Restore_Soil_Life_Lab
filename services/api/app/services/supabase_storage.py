from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from urllib import error, parse, request

from fastapi import HTTPException, UploadFile, status

from app.core.config import Settings


@dataclass(slots=True)
class UploadedStorageObject:
    bucket: str
    path: str
    public_url: str
    content_type: str | None
    byte_size: int | None


class SupabaseStorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def ensure_configured(self) -> None:
        if self.settings.has_supabase_storage:
            return
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Supabase Storage is not configured. Set SUPABASE_URL, "
                "SUPABASE_SERVICE_ROLE_KEY, and SUPABASE_STORAGE_BUCKET in the API env."
            ),
        )

    def upload_media(self, *, file: UploadFile, filename: str | None = None) -> UploadedStorageObject:
        self.ensure_configured()

        original_name = filename or file.filename or "upload"
        safe_name = _sanitize_filename(original_name)
        object_path = f"cms/{safe_name}"

        content = file.file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

        content_type = file.content_type or mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
        upload_url = (
            f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/"
            f"{self.settings.supabase_storage_bucket}/{parse.quote(object_path)}"
        )

        req = request.Request(
            upload_url,
            data=content,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.supabase_service_role_key}",
                "apikey": self.settings.supabase_service_role_key or "",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
        )

        try:
            with request.urlopen(req, timeout=20):
                pass
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            message = _parse_storage_error(detail) or "Supabase Storage upload failed."
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=message) from exc
        except error.URLError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not reach Supabase Storage.",
            ) from exc

        public_url = (
            f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/public/"
            f"{self.settings.supabase_storage_bucket}/{parse.quote(object_path)}"
        )

        return UploadedStorageObject(
            bucket=self.settings.supabase_storage_bucket,
            path=object_path,
            public_url=public_url,
            content_type=content_type,
            byte_size=len(content),
        )

    def delete_media(self, *, storage_bucket: str | None, storage_key: str | None) -> None:
        if not storage_bucket or not storage_key or not self.settings.has_supabase_storage:
            return

        delete_url = (
            f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/"
            f"{storage_bucket}"
        )
        payload = json.dumps({"prefixes": [storage_key]}).encode("utf-8")
        req = request.Request(
            delete_url,
            data=payload,
            method="DELETE",
            headers={
                "Authorization": f"Bearer {self.settings.supabase_service_role_key}",
                "apikey": self.settings.supabase_service_role_key or "",
                "Content-Type": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=20):
                pass
        except error.HTTPError:
            # Keep DB deletion resilient even if the storage file is already gone.
            return
        except error.URLError:
            return


def _sanitize_filename(value: str) -> str:
    name = Path(value).name.strip().replace(" ", "-")
    cleaned = "".join(ch for ch in name if ch.isalnum() or ch in {".", "-", "_"})
    return cleaned or "upload"


def _parse_storage_error(payload: str) -> str | None:
    if not payload:
        return None
    try:
        body = json.loads(payload)
    except json.JSONDecodeError:
        return payload.strip() or None
    return body.get("message") or body.get("error") or body.get("msg")

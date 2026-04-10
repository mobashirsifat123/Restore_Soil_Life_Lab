from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class AuthenticatedUser:
    user_id: UUID
    organization_id: UUID
    email: str
    full_name: str | None
    roles: list[str]
    permissions: set[str]

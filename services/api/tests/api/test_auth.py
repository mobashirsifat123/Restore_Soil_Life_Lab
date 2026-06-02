from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.api.dependencies.services import get_admin_service, get_auth_service, get_project_service
from app.core.config import get_settings
from app.core.errors import AppError
from app.domain.auth import AuthenticatedUser
from app.domain.permissions import Permissions
from app.schemas.admin import AdminUserListResponse
from app.schemas.auth import LoginRequest
from app.schemas.project import ProjectDetail, ProjectListResponse
from app.services.auth_service import AuthSessionResult


@dataclass(slots=True)
class FakeSessionState:
    user: AuthenticatedUser
    email: str
    password: str


class FakeAuthService:
    def __init__(self) -> None:
        self.organization_a = UUID("00000000-0000-7000-0000-000000000101")
        self.organization_b = UUID("00000000-0000-7000-0000-000000000202")
        self.states = {
            "scientist@example.com": FakeSessionState(
                user=AuthenticatedUser(
                    user_id=UUID("00000000-0000-7000-0000-000000000001"),
                    organization_id=self.organization_a,
                    email="scientist@example.com",
                    full_name="Local Scientist",
                    roles=["org_admin"],
                    permissions={
                        Permissions.PROJECT_READ,
                        Permissions.PROJECT_WRITE,
                        Permissions.SAMPLE_READ,
                        Permissions.SAMPLE_WRITE,
                        Permissions.SCENARIO_READ,
                        Permissions.SCENARIO_WRITE,
                        Permissions.RUN_READ,
                        Permissions.RUN_SUBMIT,
                    },
                ),
                email="scientist@example.com",
                password="ScientistLocal2026!",
            ),
            "member@example.com": FakeSessionState(
                user=AuthenticatedUser(
                    user_id=UUID("00000000-0000-7000-0000-000000000002"),
                    organization_id=self.organization_a,
                    email="member@example.com",
                    full_name="Local Member",
                    roles=["scientist"],
                    permissions={
                        Permissions.PROJECT_READ,
                        Permissions.PROJECT_WRITE,
                        Permissions.SAMPLE_READ,
                        Permissions.SAMPLE_WRITE,
                        Permissions.SCENARIO_READ,
                        Permissions.SCENARIO_WRITE,
                        Permissions.RUN_READ,
                        Permissions.RUN_SUBMIT,
                    },
                ),
                email="member@example.com",
                password="MemberLocal2026!",
            )
        }
        self.active_tokens: dict[str, AuthenticatedUser] = {}
        self.next_token = 1

    def login(
        self,
        *,
        payload: LoginRequest,
        user_agent: str | None,
        ip_address: str | None,
    ) -> AuthSessionResult:
        state = self.states.get(payload.email)
        if state is None or payload.password != state.password:
            raise AppError(
                status_code=401,
                code="invalid_credentials",
                message="Invalid email or password.",
            )
        if payload.organization_id and payload.organization_id != state.user.organization_id:
            raise AppError(
                status_code=403,
                code="organization_access_denied",
                message="You do not have access to the requested organization.",
                details={"organizationId": str(payload.organization_id)},
            )

        session_token = f"token-{self.next_token}"
        self.next_token += 1
        self.active_tokens[session_token] = state.user
        return AuthSessionResult(
            session=self.build_session(state.user),
            session_token=session_token,
        )

    def authenticate_request(self, request: Request) -> AuthenticatedUser:
        session_token = request.cookies.get("bio_session")
        if not session_token or session_token not in self.active_tokens:
            raise AppError(
                status_code=401,
                code="auth_required",
                message="Authentication is required.",
            )
        return self.active_tokens[session_token]

    def logout(self, request: Request) -> None:
        session_token = request.cookies.get("bio_session")
        if session_token:
            self.active_tokens.pop(session_token, None)

    def build_session(self, current_user: AuthenticatedUser):
        from app.services.auth_service import AuthService

        stub = object.__new__(AuthService)
        return AuthService.build_session(stub, current_user)


class FakeProjectService:
    def list_projects(
        self,
        *,
        current_user: AuthenticatedUser,
        limit: int,
        cursor: str | None,
    ) -> ProjectListResponse:
        project_id = uuid4()
        label = "Org A Project" if current_user.organization_id.int % 2 else "Org B Project"
        return ProjectListResponse(
            items=[
                ProjectDetail(
                    id=project_id,
                    organization_id=current_user.organization_id,
                    name=label,
                    slug=label.lower().replace(" ", "-"),
                    description=None,
                    status="active",
                    metadata={},
                    created_at="2026-04-01T00:00:00Z",
                    updated_at="2026-04-01T00:00:00Z",
                )
            ],
            next_cursor=None,
        )


class FakeAdminService:
    def list_users(self, *, current_user: AuthenticatedUser) -> AdminUserListResponse:
        return AdminUserListResponse(items=[])


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/bio_lab")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    get_settings.cache_clear()
    from app.main import create_application

    auth_service = FakeAuthService()
    app = create_application()
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    app.dependency_overrides[get_project_service] = lambda: FakeProjectService()
    app.dependency_overrides[get_admin_service] = lambda: FakeAdminService()

    with TestClient(app) as client:
        yield SimpleNamespace(client=client, auth_service=auth_service, app=app)

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_login_sets_session_cookie_and_session_endpoint_returns_identity(auth_client) -> None:
    response = auth_client.client.post(
        "/api/v1/auth/login",
        json={"email": "scientist@example.com", "password": "ScientistLocal2026!"},
    )

    assert response.status_code == 200
    assert "bio_session=" in response.headers["set-cookie"]
    assert response.json()["user"]["email"] == "scientist@example.com"

    session_response = auth_client.client.get("/api/v1/auth/session")

    assert session_response.status_code == 200
    assert session_response.json()["activeOrganizationId"] == str(
        auth_client.auth_service.organization_a
    )


def test_login_does_not_mark_cookie_secure_for_http_requests(
    auth_client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTH_SESSION_SECURE_COOKIE", "true")
    get_settings.cache_clear()

    response = auth_client.client.post(
        "/api/v1/auth/login",
        json={"email": "scientist@example.com", "password": "ScientistLocal2026!"},
    )

    assert response.status_code == 200
    assert "bio_session=" in response.headers["set-cookie"]
    assert "Secure" not in response.headers["set-cookie"]


def test_login_rejects_requested_organization_without_membership(auth_client) -> None:
    response = auth_client.client.post(
        "/api/v1/auth/login",
        json={
            "email": "scientist@example.com",
            "password": "ScientistLocal2026!",
            "organizationId": str(auth_client.auth_service.organization_b),
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "organization_access_denied"


def test_logout_revokes_session_cookie(auth_client) -> None:
    auth_client.client.post(
        "/api/v1/auth/login",
        json={"email": "scientist@example.com", "password": "ScientistLocal2026!"},
    )

    logout_response = auth_client.client.post("/api/v1/auth/logout")

    assert logout_response.status_code == 204

    session_response = auth_client.client.get("/api/v1/auth/session")
    assert session_response.status_code == 401


def test_project_routes_use_authenticated_organization_scope(auth_client) -> None:
    auth_client.client.post(
        "/api/v1/auth/login",
        json={"email": "scientist@example.com", "password": "ScientistLocal2026!"},
    )

    response = auth_client.client.get("/api/v1/projects")

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["organizationId"] == str(auth_client.auth_service.organization_a)


def test_admin_routes_require_org_admin_role(auth_client) -> None:
    auth_client.client.post(
        "/api/v1/auth/login",
        json={"email": "member@example.com", "password": "MemberLocal2026!"},
    )

    response = auth_client.client.get("/api/v1/admin/users")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "admin_required"


def test_admin_routes_allow_org_admin_role(auth_client) -> None:
    auth_client.client.post(
        "/api/v1/auth/login",
        json={"email": "scientist@example.com", "password": "ScientistLocal2026!"},
    )

    response = auth_client.client.get("/api/v1/admin/users")

    assert response.status_code == 200

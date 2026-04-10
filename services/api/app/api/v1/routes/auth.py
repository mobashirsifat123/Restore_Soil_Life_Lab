from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies.auth import CurrentUser
from app.api.dependencies.services import get_auth_service
from app.core.config import get_settings
from app.schemas.auth import (
    AuthSessionListResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MemberProfileResponse,
    RegisterRequest,
    ResetPasswordRequest,
    SessionResponse,
    UpdateMemberProfileRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/login",
    response_model=SessionResponse,
    operation_id="auth_login",
    summary="Create an authenticated session",
)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthServiceDependency,
) -> SessionResponse:
    settings = get_settings()
    session = auth_service.login(
        payload=payload,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=session.session_token,
        httponly=True,
        max_age=settings.auth_session_ttl_hours * 60 * 60,
        secure=settings.auth_session_secure_cookie,
        samesite="lax",
        path="/",
    )
    return session.session


@router.post(
    "/register",
    response_model=SessionResponse,
    operation_id="auth_register",
    summary="Create a new user and session",
)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    auth_service: AuthServiceDependency,
) -> SessionResponse:
    settings = get_settings()
    session = auth_service.register(
        payload=payload,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    response.set_cookie(
        key=settings.auth_session_cookie_name,
        value=session.session_token,
        httponly=True,
        max_age=settings.auth_session_ttl_hours * 60 * 60,
        secure=settings.auth_session_secure_cookie,
        samesite="lax",
        path="/",
    )
    return session.session


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    operation_id="auth_forgotPassword",
    summary="Generate a password recovery code",
)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    auth_service: AuthServiceDependency,
) -> ForgotPasswordResponse:
    return auth_service.forgot_password(
        payload=payload,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="auth_resetPassword",
    summary="Reset the password using a recovery code",
)
def reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthServiceDependency,
) -> Response:
    auth_service.reset_password(payload=payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="auth_logout",
    summary="Clear the current authenticated session",
)
def logout(
    request: Request,
    response: Response,
    auth_service: AuthServiceDependency,
) -> Response:
    settings = get_settings()
    auth_service.logout(request)
    response.delete_cookie(
        key=settings.auth_session_cookie_name,
        secure=settings.auth_session_secure_cookie,
        samesite="lax",
        path="/",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get(
    "/session",
    response_model=SessionResponse,
    operation_id="auth_getSession",
    summary="Get the current authenticated session",
)
def get_session(
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> SessionResponse:
    return auth_service.build_session(current_user)


@router.get(
    "/profile",
    response_model=MemberProfileResponse,
    operation_id="auth_getProfile",
    summary="Get the current member profile",
)
def get_profile(
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> MemberProfileResponse:
    return auth_service.get_profile(current_user)


@router.patch(
    "/profile",
    response_model=MemberProfileResponse,
    operation_id="auth_updateProfile",
    summary="Update the current member profile",
)
def update_profile(
    payload: UpdateMemberProfileRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> MemberProfileResponse:
    return auth_service.update_profile(current_user=current_user, payload=payload)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="auth_changePassword",
    summary="Change the current member password",
)
def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> Response:
    auth_service.change_password(current_user=current_user, payload=payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/sessions",
    response_model=AuthSessionListResponse,
    operation_id="auth_listSessions",
    summary="List active sessions for the current member",
)
def list_sessions(
    request: Request,
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> AuthSessionListResponse:
    return auth_service.list_sessions(request, current_user)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="auth_revokeSession",
    summary="Revoke one of the current member's sessions",
)
def revoke_session(
    session_id: str,
    request: Request,
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> Response:
    from uuid import UUID

    auth_service.revoke_session_by_id(
        current_user=current_user,
        session_id=UUID(session_id),
        request=request,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sessions/revoke-others",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="auth_revokeOtherSessions",
    summary="Revoke all other active sessions for the current member",
)
def revoke_other_sessions(
    request: Request,
    current_user: CurrentUser,
    auth_service: AuthServiceDependency,
) -> Response:
    auth_service.revoke_other_sessions(current_user=current_user, request=request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

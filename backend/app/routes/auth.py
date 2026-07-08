from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import Settings, get_settings
from app.core.security import create_token, get_current_user, CurrentUser
from app.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, settings: Settings = Depends(get_settings)):
    email = payload.email.strip().lower()
    role = None
    if email == settings.demo_admin_email.lower() and payload.password == settings.demo_admin_password:
        role = "admin"
    elif email == settings.demo_user_email.lower() and payload.password == settings.demo_user_password:
        role = "user"
    if role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo credentials")
    return LoginResponse(
        access_token=create_token(email, role, settings),
        role=role,
        email=email,
        auth_enabled=settings.auth_enabled,
    )


@router.get("/me")
def me(user: CurrentUser = Depends(get_current_user), settings: Settings = Depends(get_settings)):
    return {"email": user.email, "role": user.role, "auth_enabled": settings.auth_enabled}

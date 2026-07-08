import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from fastapi import Header, HTTPException, status, Depends
from app.core.config import get_settings, Settings


@dataclass
class CurrentUser:
    email: str
    role: str


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def _sign(payload_b64: str, secret: str) -> str:
    return _b64url_encode(hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest())


def create_token(email: str, role: str, settings: Settings) -> str:
    payload = {
        "sub": email,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + settings.token_expire_minutes * 60,
    }
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _sign(payload_b64, settings.jwt_secret)
    return f"{payload_b64}.{signature}"


def decode_token(token: str, settings: Settings) -> CurrentUser:
    try:
        payload_b64, signature = token.split(".", 1)
        expected = _sign(payload_b64, settings.jwt_secret)
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        payload = json.loads(_b64url_decode(payload_b64))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired token")
        return CurrentUser(email=str(payload["sub"]), role=str(payload["role"]))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


def require_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    """Optional API-key protection.

    If APP_API_KEY is empty, local development is open.
    If APP_API_KEY is set, clients must send X-API-Key.
    """
    if not settings.app_api_key:
        return
    if x_api_key != settings.app_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")


def get_current_user(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    """Optional demo auth.

    For local development AUTH_ENABLED=false returns a demo admin, so the app remains easy
    to run. Set AUTH_ENABLED=true in deployment to require Bearer tokens from /api/auth/login.
    """
    if not settings.auth_enabled:
        return CurrentUser(email=settings.demo_admin_email, role="admin")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    return decode_token(token, settings)


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user

"""Simple single-user authentication with expiring server-side sessions."""

import secrets
import threading
import time
from typing import Dict, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from config.settings import settings

auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])
SESSION_COOKIE = "supply_chain_session"
_sessions: Dict[str, Tuple[str, float]] = {}
_sessions_lock = threading.Lock()


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=256)


def _valid_credentials(email: str, password: str) -> bool:
    valid_email = secrets.compare_digest(email, settings.AUTH_USERNAME)
    valid_password = secrets.compare_digest(password, settings.AUTH_PASSWORD)
    return valid_email and valid_password


def get_current_user(request: Request) -> str:
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        raise HTTPException(status_code=401, detail="Sign in required")

    now = time.time()
    with _sessions_lock:
        session = _sessions.get(session_id)
        if session and session[1] > now:
            return session[0]
        _sessions.pop(session_id, None)

    raise HTTPException(status_code=401, detail="Session expired; sign in again")


@auth_router.post("/login")
def login(payload: LoginRequest, response: Response) -> Dict[str, str]:
    if not _valid_credentials(payload.email, payload.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    session_id = secrets.token_urlsafe(32)
    with _sessions_lock:
        _sessions[session_id] = (settings.AUTH_USERNAME, time.time() + settings.SESSION_TTL_SECONDS)

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        max_age=settings.SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return {"user": settings.AUTH_USERNAME}


@auth_router.post("/logout")
def logout(request: Request, response: Response) -> Dict[str, bool]:
    session_id = request.cookies.get(SESSION_COOKIE)
    if session_id:
        with _sessions_lock:
            _sessions.pop(session_id, None)
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax")
    return {"ok": True}


@auth_router.get("/me")
def current_user(user: str = Depends(get_current_user)) -> Dict[str, str]:
    return {"user": user}
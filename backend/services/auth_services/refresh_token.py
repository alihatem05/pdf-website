import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from models.refresh_token import RefreshToken
from config import REFRESH_TOKEN_LONG_DAYS, REFRESH_TOKEN_SHORT_DAYS

def generate_refresh_token() -> str:
  return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
  return hashlib.sha256(token.encode()).hexdigest()

async def create_refresh_token(db: AsyncSession, response: Response, user_id, remember_me: bool = False) -> None:
    raw_token = generate_refresh_token()
    days = REFRESH_TOKEN_LONG_DAYS if remember_me else REFRESH_TOKEN_SHORT_DAYS
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)

    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            expires_at=expires_at,
        )
    )
    await db.commit()

    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=days * 24 * 60 * 60,
        path="/api/auth/refresh",
    )
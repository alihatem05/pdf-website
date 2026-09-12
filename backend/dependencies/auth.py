import uuid
from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from backend.database import get_db
from backend.models.user import User
from backend.services.auth.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(credentials=Depends(bearer_scheme), db=Depends(get_db)):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(credentials.credentials)
        if payload is None:
            raise ValueError("invalid or expired token")
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("missing sub")
        user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
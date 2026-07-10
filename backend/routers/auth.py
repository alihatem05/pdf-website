from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.user import User
from models.refresh_token import RefreshToken
from schemas.user import UserLogin, UserRead, UserRegister
from schemas.login import LoginRead
from services.auth_services.jwt import create_access_token
from services.auth_services.password import hash_password, verify_password
from services.auth_services.refresh_token import generate_refresh_token, hash_token, create_refresh_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=LoginRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, response: Response, db: AsyncSession = Depends(get_db)):
    existing_user = await db.scalar(
        select(User).where((User.email == user_data.email) | (User.username == user_data.username))
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that email or username already exists",
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(new_user.id)
    await create_refresh_token(db, response, new_user.id, remember_me=False)
    await db.refresh(new_user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user,
    }


@router.post("/login", response_model=LoginRead, status_code=status.HTTP_200_OK)
async def login(user_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == user_data.email))

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)
    await create_refresh_token(db, response, user.id, remember_me=user_data.remember_me)
    await db.refresh(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token))
    )
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.revoked or db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    db_token.revoked = True
    remaining = db_token.expires_at - datetime.now(timezone.utc)

    new_raw_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=db_token.user_id,
            token_hash=hash_token(new_raw_token),
            expires_at=db_token.expires_at,
        )
    )
    await db.commit()

    access_token = create_access_token(db_token.user_id)

    response.set_cookie(
        key="refresh_token",
        value=new_raw_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(remaining.total_seconds()),
        path="/api/auth/refresh",
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    raw_token = request.cookies.get("refresh_token")
    if raw_token:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token))
        )
        if db_token := result.scalar_one_or_none():
            db_token.revoked = True
            await db.commit()

    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return {"detail": "Logged out"}
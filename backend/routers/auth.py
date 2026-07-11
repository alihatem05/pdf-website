from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.user import User
from models.refresh_token import RefreshToken
from schemas.user import UserLogin, UserRegister
from schemas.login import LoginRead
from schemas.auth import PasswordChange
from services.auth_services.jwt import create_access_token
from services.auth_services.password import hash_password, verify_password
from services.auth_services.refresh_token import hash_token, create_refresh_token, rotate_refresh_token, revoke_all_refresh_tokens
from dependencies.auth import get_current_user  

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
    await create_refresh_token(db, response, new_user.id, remember_me=user_data.remember_me)
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

    if not db_token or db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    remaining = db_token.expires_at - datetime.now(timezone.utc)
    new_raw_token = await rotate_refresh_token(db, db_token)
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
        await db.execute(
            delete(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_token))
        )
        await db.commit()

    response.delete_cookie("refresh_token", path="/api/auth/refresh")
    return {"detail": "Logged out"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    data: PasswordChange,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = hash_password(data.new_password)
    await revoke_all_refresh_tokens(db, current_user.id)
    await db.commit()

    response.delete_cookie("refresh_token", path="/api/auth/refresh")

    return {"detail": "Password changed. Please log in again."}
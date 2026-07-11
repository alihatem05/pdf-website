from fastapi import APIRouter, Depends
from models.user import User
from schemas.user import UserRead
from dependencies.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
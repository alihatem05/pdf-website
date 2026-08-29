from fastapi import APIRouter, Depends
from backend.dependencies.auth import get_current_user
from backend.models.user import User
from backend.schemas.user import UserRead

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

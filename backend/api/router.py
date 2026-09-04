from fastapi import APIRouter
from backend.api.controllers.auth_controller import router as auth_router
from backend.api.controllers.user_controller import router as users_router
from backend.api.controllers.chat_controller import router as chats_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(chats_router)
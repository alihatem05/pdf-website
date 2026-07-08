from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from .user import UserRead

class LoginRead(BaseModel):
    access_token: str
    token_type: str
    user: UserRead
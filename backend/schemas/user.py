from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    remember_me: bool = False

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
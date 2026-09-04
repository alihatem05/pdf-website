from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=25)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
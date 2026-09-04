from pydantic import BaseModel
from .user import UserRead

class LoginRead(BaseModel):
    access_token: str
    token_type: str
    user: UserRead
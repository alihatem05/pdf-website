from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from config import JWT_SECRET, ALGORITHM, JWT_EXPIRY_TIME

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_TIME)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=ALGORITHM
    )

    return token

def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None
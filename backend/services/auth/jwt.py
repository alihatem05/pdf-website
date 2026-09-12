from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.config import JWT_SECRET, ALGORITHM, JWT_EXPIRY_TIME


def create_access_token(user_id):
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRY_TIME)

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None

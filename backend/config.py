from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRY_TIME = int(os.getenv("JWT_EXPIRY_TIME", "30"))
FRONTEND_URL = os.getenv("FRONTEND_URL")
REFRESH_TOKEN_LONG_DAYS = int(os.getenv("REFRESH_TOKEN_LONG_DAYS"))
REFRESH_TOKEN_SHORT_DAYS = int(os.getenv("REFRESH_TOKEN_SHORT_DAYS"))
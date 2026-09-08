from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CELERY_DATABASE_URL = os.getenv("CELERY_DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRY_TIME = int(os.getenv("JWT_EXPIRY_TIME", "7"))
FRONTEND_URL = os.getenv("FRONTEND_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().with_name(".env"))

DATABASE_URL = os.getenv("DATABASE_URL")
CELERY_DATABASE_URL = os.getenv("CELERY_DATABASE_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRY_TIME = int(os.getenv("JWT_EXPIRY_TIME", "7"))
FRONTEND_URL = os.getenv("FRONTEND_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))
LLM_TOP_K = int(os.getenv("LLM_TOP_K", "4"))
SUMMARY_LIMIT = int(os.getenv("SUMMARY_LIMIT", "20"))
SUMMARY_THRESHOLD = int(os.getenv("SUMMARY_THRESHOLD", "10"))
CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "12"))
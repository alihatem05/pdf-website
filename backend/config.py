import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
CELERY_DATABASE_URL = os.getenv("CELERY_DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
JWT_EXPIRY_TIME = int(os.getenv("JWT_EXPIRY_TIME", "7"))
FRONTEND_URL = os.getenv("FRONTEND_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
SUMMARY_THRESHOLD = int(os.getenv("SUMMARY_THRESHOLD", "10"))
CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "12"))
LLM_TOP_K = int(os.getenv("LLM_TOP_K", "8"))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))
SUMMARY_LIMIT = int(os.getenv("SUMMARY_LIMIT", "20"))

S3_BUCKET = os.getenv("S3_BUCKET")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_REGION = os.getenv("S3_REGION")
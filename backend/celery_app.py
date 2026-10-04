from celery import Celery
from config import REDIS_URL

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.imports = (
    "services.llm.embed",
    "services.llm.summarize",
)
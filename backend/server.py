from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from config import FRONTEND_URL
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

app = FastAPI(title="PDF Website API")

@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/api")
async def api_root():
    return {"message": "Test!"}


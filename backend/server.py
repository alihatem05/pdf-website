from fastapi import FastAPI
from routers.auth import router as auth_router

app = FastAPI(title="PDF Website API")

app.include_router(auth_router)

@app.get("/api")
async def api_root():
    return {"message": "Test!"}


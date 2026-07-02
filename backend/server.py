from fastapi import FastAPI

app = FastAPI()

@app.get("/api")
async def api_root():
    return {"message": "Test!"}
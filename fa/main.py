from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import uvicorn
from redis.asyncio import Redis

from src.database.redis_db import get_async_redis_client
from src.routes import contacts, auth, users


app = FastAPI()

app.include_router(contacts.router)
app.include_router(auth.router)
app.include_router(users.router)


@app.on_event("startup")
async def startup():
    redis_client = await get_async_redis_client()
    await FastAPILimiter.init(redis_client)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
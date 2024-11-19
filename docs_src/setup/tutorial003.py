from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

app = APIRouter()


@app.get("/index", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def index():
    return {"msg": "Hello World"}

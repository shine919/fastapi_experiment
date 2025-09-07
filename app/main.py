from contextlib import asynccontextmanager

import redis.asyncio as redis
from babel import babel_configs
from core.config import settings
from exceptions import ExceptionHandlers
from fastapi import FastAPI
from fastapi_babel import BabelMiddleware
from fastapi_limiter import FastAPILimiter
from router import router
from sub_app.api_2 import sub_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # con = redis.Redis(host="redis", port=6379, db=0) #  docker
    con = redis.Redis(host="127.0.0.1", db=0)  # dev
    await FastAPILimiter.init(con)
    yield


app = FastAPI(root_path="/api/v1", redoc_url=None, docs_url=None, openapi_url=None, lifespan=lifespan)
app.include_router(router)
app.mount("/sub_app/", sub_app)
# Добавляем мидлварь, который будет устанавливать локаль для каждого запроса
app.add_middleware(BabelMiddleware, babel_configs=babel_configs)

if settings.mode == "DEV":
    app.debug = True
else:
    app.debug = False


@app.get("/")
async def root():
    return {"message": "hello"}


ExceptionHandlers.register_all(app)

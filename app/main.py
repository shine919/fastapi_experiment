import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware, _
from pydantic import BaseModel
import redis.asyncio as redis
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from core.config import settings, mini_db
from fastapi import FastAPI, HTTPException, Depends,Request
from fastapi.responses import JSONResponse
from logger import logger
from router import router
from security import create_tokens, ALGORITHM


logging.basicConfig(level=logging.INFO)
security = HTTPBasic()

@asynccontextmanager
async def lifespan(app:FastAPI):
    # con = redis.Redis(host="redis", port=6379, db=0) #  docker
    con = redis.Redis(host="127.0.0.1") # dev
    await FastAPILimiter.init(con)
    yield

app = FastAPI(redoc_url=None, docs_url=None, openapi_url=None,lifespan=lifespan)
app.include_router(router)

if settings.debug:
    app.debug = True
else:
    app.debug = False

class CustomExceptionModel(BaseModel):
    status_code: int
    er_message: str
    er_details: str

class CustomException(HTTPException):
    def __init__(self,  status_code: int, detail: str,message:str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message
# Кастомный обработчик для ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": [
                {
                    "field": err["loc"][-1],
                    "message": err["msg"]
                }
                for err in exc.errors()
            ]
        }
    )

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    error = jsonable_encoder(CustomExceptionModel(status_code=exc.status_code, er_message=exc.message, er_details=exc.detail))
    return JSONResponse(status_code=exc.status_code, content=error)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Caught exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error "}
    )



# # Создаем объект конфигурации для Babel:
# babel_configs = BabelConfigs(
#     ROOT_DIR=Path(__file__).resolve().parent,
#     BABEL_DEFAULT_LOCALE="en",  # Язык по умолчанию
#     BABEL_TRANSLATION_DIRECTORY="locales"  # Папка с переводами
# )
#
# # Инициализируем объект Babel с использованием конфигурации
# babel = Babel(configs=babel_configs)
#
# # Добавляем мидлварь, который будет устанавливать локаль для каждого запроса
# app.add_middleware(BabelMiddleware, babel_configs=babel_configs)



class UserNotFoundException(HTTPException):
    def __init__(self,status_code:int,detail:str):
        super().__init__(status_code=status_code, detail=detail)
        self.time = datetime.now()



class ErrorResponseModel(BaseModel):
    status_code : int
    message:str
    error_code:str
    time : str

@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException) -> JSONResponse:
    await asyncio.sleep(2)
    error = jsonable_encoder(ErrorResponseModel(status_code=exc.status_code, message=exc.detail, error_code="USER_NOT_FOUND",time=str(datetime.now() - exc.time)))

    print(str(datetime.now() - exc.time))
    return JSONResponse(status_code=exc.status_code, content=error)
@app.get("/name")
async def timing(a:int):
    if a == 5:
        raise UserNotFoundException(status_code=404,detail="User not found")
    return {"a":a}





@app.get("/")
async def root():

    return {'message': 'hello'}






@app.get("/sum/")
def calculate_sum(a: int, b: int):
    return {"result": a + b}































@app.post("/refresh",dependencies=[Depends(RateLimiter(times=5,minutes=1))])
async def refresh(refresh_token  : str):
    data = jwt.decode(refresh_token, settings.secret_key, algorithms=[ALGORITHM])
    if data.get("type",None):
        if data.get('exp') > datetime.now().timestamp():
            for user in mini_db:
                if user[data.get("sub")]:
                    return await create_tokens({"sub":data.get("sub")})
                raise HTTPException(status_code=401, detail="Token not found")
        raise  HTTPException(status_code=401, detail="Token is expired")
    raise HTTPException(status_code=401, detail="Incorrect token")







# async def hide_doc(credentials: HTTPBasicCredentials = Depends(security)):
#     # if settings.mode == "DEV":
#     #     if secrets.compare_digest(credentials.username, settings.super_user.USERNAME) and secrets.compare_digest(credentials.password, settings.super_user.PASSWORD):
#     #         return
#     #     raise HTTPException(status_code=401, detail="Incorrect username or password",headers={"WWW-Authenticate": "Basic"})
#     # raise HTTPException(status_code=404, detail="Not Found")
#     return True # dev


@app.get("/docs",include_in_schema=False,)
async def custom_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json",title="docs")

@app.get("/openapi.json",include_in_schema=False,)
async def openapi_json():
    return get_openapi(title="FastAPI", version="0.1.0", routes=app.routes)
#
#
#
# @app.get("/headers")
# async def get_headers(headers :CommonHeaders = Header()):
#
#     if headers.user_agent and headers.accept_language and headers.x_current_version:
#         return {
#         "User-Agent": headers.user_agent,
#         "Accept-Language": headers.accept_language,
#         "X-Current-Version": headers.x_current_version,
#     }
#     else:
#         raise HTTPException(status_code=400, detail="Headers are invalid")
#
# @app.get("/info")
# async def get_info(response:Response,headers :CommonHeaders = Header(),):
#     if headers.user_agent and headers.accept_language:
#         response.headers["X-Server-Time"] = str(datetime.now().timestamp())
#         return {
#         "Headers": {
#             "User-Agent": headers.user_agent,
#             "Accept-Language": headers.accept_language,
#         },
#         "Message": "Добро пожаловать! Ваши заголовки успешно обработаны."
#     }
#     else:
#         raise HTTPException(status_code=400, detail="Headers are invalid")
#
#
#
#
#
# @app.post("/itemspg")
# async def create_item(item: Item,session: AsyncSession = Depends(get_session)):
#     # result = await session.execute(text(
#     #     "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,name TEXT NOT NULL)"))
#     # await session.commit()
#     await session.execute(text(f"INSERT INTO items (name) VALUES ('{item.name}')"))
#     await session.commit()
#
#     return {"message": "Item added successfully!"}
#
# @app.post("/items")
# async def create_item(item: Item, db: AsyncIOMotorDatabase = Depends(get_db)):
#     result = await db.items.insert_one(item.model_dump())
#     return {"message": "Item added successfully!", "id": str(result.inserted_id)}



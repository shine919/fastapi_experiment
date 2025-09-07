import secrets

from core.config import settings
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

router = APIRouter()


async def hide_doc(credentials: HTTPBasicCredentials = Depends(security)):
    if settings.mode != "DEV":
        if secrets.compare_digest(credentials.username, settings.super_user.USERNAME) and secrets.compare_digest(
            credentials.password, settings.super_user.PASSWORD
        ):
            return
        raise HTTPException(
            status_code=401, detail="Incorrect username or password", headers={"WWW-Authenticate": "Basic"}
        )
    return


@router.get(
    "/docs",
    include_in_schema=False,
)
async def custom_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@router.get(
    "/openapi.json",
    include_in_schema=False,
    dependencies=[
        Depends(hide_doc),
    ],
)
async def openapi_json(request: Request):
    return get_openapi(title="FastAPI", version="0.1.0", routes=request.app.routes)

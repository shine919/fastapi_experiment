from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ExceptionHandlers:
    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": [{"field": err["loc"][-1], "message": err["msg"]} for err in exc.errors()],
            },
        )

    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception):
        print(f"Caught exception: {exc}")
        return JSONResponse(status_code=500, content={"error": "Internal server error "})

    @classmethod
    def register_all(cls, app: FastAPI):
        app.add_exception_handler(RequestValidationError, cls.validation_exception_handler)
        app.add_exception_handler(Exception, cls.global_exception_handler)

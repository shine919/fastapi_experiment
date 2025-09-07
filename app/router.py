from docs import router as docs_router
from fastapi import APIRouter
from todo.views import router as todo_router
from user.views import router as user_router

router = APIRouter()

router.include_router(todo_router)
router.include_router(user_router)

router.include_router(docs_router)

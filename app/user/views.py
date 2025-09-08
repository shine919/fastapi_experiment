from typing import Annotated

from db import get_session, resources
from fastapi import APIRouter, Body, Depends, Form, Header, Request
from fastapi_limiter.depends import RateLimiter
from rbac import AccessToDataChecker, PermissionChecker
from security import PayloadFromJWT, TokenManager, get_token_manager
from sqlalchemy.ext.asyncio import AsyncSession
from user.auth import login_user_auth
from user.crud import UserOrm
from user.schema import UserLogin, UserPatch, UserPut, UserRegister
from utils import get_current_user

router = APIRouter(tags=["User"], prefix="/users")


@router.post("/register", dependencies=[Depends(RateLimiter(times=50, minutes=1))])
async def register_user(user: UserRegister, session: AsyncSession = Depends(get_session)):
    await UserOrm.register_user_orm(user, session)
    return "User successfully registered"


@router.post("/login")
async def login_user(
    request: Request,
    user: UserLogin = Form(),
    user_agent: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_session),
    manager: TokenManager = Depends(get_token_manager),
):
    tokens = await login_user_auth(user, session, request, user_agent, manager)
    return tokens


@router.get("/get_users/")
async def get_all_users(session: AsyncSession = Depends(get_session)):
    return await UserOrm.get_users_orm(session)


@router.post("/refresh/")
async def refresh_tokens(
    refresh_token: str, client_ip: str, user_agent: str, manager: TokenManager = Depends(get_token_manager)
):
    return await manager.take_new_refresh(refresh_token, client_ip, user_agent)


@router.delete("/user/{user_id}/")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    return await UserOrm.delete_user_orm(user_id, session)


@router.get("/user/{user_id}/")
async def get_user_by_id(user_id: int, session: AsyncSession = Depends(get_session)):
    return await UserOrm.check_user_orm(session, user_id=user_id)


@router.put("/user/{user_id}")
async def put_update_user(user_id: int, user: UserPut, session: AsyncSession = Depends(get_session)):
    await UserOrm.put_user_orm(user_id, user, session)

    return {f"The user with id {user.id} was updated successfully!"}


@router.patch("/user/{user_id}")
async def patch_update_user(user_id: int, user: UserPatch = Body(), session: AsyncSession = Depends(get_session)):
    result = await UserOrm.patch_user_orm(user_id, user, session)

    return {f"The user with id {user_id} was updated successfully!{result}"}


@router.get("/protected_resource/{username}")
@AccessToDataChecker("GET")
@PermissionChecker(["user"])
async def information_get(username: str, user_payload: PayloadFromJWT = Depends(get_current_user)):
    print(f"hello {username}")
    return resources[username]["content"]


# @router.get("/admin")
# @PermissionChecker(["admin"])
# async def admin_info(current_user: UserFromDB = Depends(get_current_user)):
#     """Маршрут для администраторов"""
#     return {"message": f"Hello, {current_user.username}! Welcome to the admin page."}
#
# @router.get("/user")
# @PermissionChecker(["user"])
# async def user_info(current_user: UserFromDB = Depends(get_current_user),_:None = Depends(get_limit_time_by_role)):
#     """Маршрут для пользователей"""
#     return {"message": f"Hello, {current_user.username}! Welcome to the user page."}

# @router.get("/about_me")
# async def about_me(current_user: UserFromDB = Depends(get_current_user)):
#     """Информация о текущем пользователе"""
#     return current_user
# @router.get("/protected_resource")
# async def information_get(token : str):
#     if token:
#         access = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
#         if access.get("type") == 'access':
#             user = await get_user_from_token(token)
#             return {"message":user}
#         raise HTTPException(status_code=401, detail="Incorrect token")
#     else:
#         raise HTTPException(status_code=401, detail="Incorrect token")

# @router.post("/protected_resource/{username}")
# @AccessToDataChecker("POST")
# @PermissionChecker(["user"])
# async def information_get(username : str,content:str= Body(...),is_public:bool = Body(False),current_user : UserFromDB = Depends(get_current_user)):
#     await add_resource(username, content,is_public)
#     return resources[username]['content']
# #
# @router.patch("/protected_resource/{username}")
# @AccessToDataChecker("PATCH")
# @PermissionChecker(["user"])
# async def information_get(username : str,content:str= Body(...),is_public:bool = Body(None),current_user : UserFromDB = Depends(get_current_user)):
#     await patch_resourse(username, content,is_public)
#     print(resources[username])
#     return resources[username]['content']
# @router.delete("/protected_resource/{username}")
# @AccessToDataChecker("PATCH")
# @PermissionChecker(["user"])
# async def information_get(username : str,current_user : UserFromDB = Depends(get_current_user)):
#     await delete_resource(username)
#
#     return 'delete succesfully'

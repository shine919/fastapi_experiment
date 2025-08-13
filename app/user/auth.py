from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from security import crypt_context, create_tokens
from user.crud import UserOrm
from user.schema import UserLogin


async def login_user_auth(user: UserLogin, session: AsyncSession):
    user_in = await UserOrm.check_user_orm(username=user.username, session=session)

    if not user_in:

        raise HTTPException(status_code=401, detail="Incorrect username or password")

    if not crypt_context.verify(user.password, user_in.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    tokens = await create_tokens({"sub": user.username})

    return {
        'access_token': tokens["access_token"],
        # 'refresh_token': tokens["refresh_token"],
        'token_type': 'bearer'
    }
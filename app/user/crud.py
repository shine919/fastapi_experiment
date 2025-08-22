from fastapi import HTTPException
from sqlalchemy import select, text, and_, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import User as UserModel
from security import crypt_context
from user.schema import UserRegister, UserCheck, UsersFromDBList, UserPut, UserPatch


async def handle_user_result(result,register:bool):
    if register and result:
        raise HTTPException(status_code=409, detail="User with this name already exists")
    if register and not result:
        return None
    if result:
        return UserCheck.model_validate(result)
    raise HTTPException(status_code=404, detail="User not found")

class UserOrm:

    @staticmethod
    async def check_user_orm(session: AsyncSession,  username: str | None = None,user_id: int | None = None,register:bool = False ):
        filters =[]
        if user_id is not None:
            filters.append(UserModel.id == user_id)
        if username is not None:
            filters.append(UserModel.username == username)
        stmt = select(UserModel).where(and_(*filters))
        query = await session.execute(stmt)
        result = query.scalars().one_or_none()
        return await handle_user_result(result,register)

    @staticmethod
    async def register_user_orm(user: UserRegister, session: AsyncSession):
        await UserOrm.check_user_orm(username=user.username, session=session, register=True)
        hashed_password = crypt_context.hash(user.password)
        stmt = insert(UserModel).values(username=user.username,password=hashed_password,email=user.email)
        query = await session.execute(stmt)
        await session.commit()
        return
    @staticmethod
    async def delete_user_orm(user_id: int, session: AsyncSession):
        await UserOrm.check_user_orm(session=session, user_id=user_id)
        stmt = delete(UserModel).where(UserModel.id == user_id)
        res = await session.execute(stmt)
        await session.commit()
        return {"message": "User deleted successfully!"}

    @staticmethod
    async def get_users_orm(session: AsyncSession):
        try:
            stmt = select(UserModel)
            query = await session.execute(stmt)
            result = query.scalars().all()
            dicts = [UserCheck.model_validate(r) for r in result]
            if dicts:
                lists = UsersFromDBList(users=dicts)
                return lists
            raise HTTPException(status_code=404, detail="Users not found")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail='Server error')

    @staticmethod
    async def put_user_orm(user:UserPut, session:AsyncSession):
        hashed_password = crypt_context.hash(user.password)
        stmt = update(UserModel).where(UserModel.id == user.id).values(username=user.username,email=user.email,password=hashed_password).returning(UserModel.username)
        query = await session.execute(stmt)
        return query.scalars().one()

    @staticmethod
    async def patch_user_orm(user:UserPatch,session:AsyncSession):
        values = {}
        if user.username:
            values['username'] = user.username
        if user.password:
            values['password'] =  crypt_context.hash(user.password)
        if user.email:
            values['email'] = user.email
        stmt = update(UserModel).where(UserModel.id==user.id).values(**values).returning(UserModel.username)
        query = await session.execute(stmt)
        await session.commit()
        return query.scalars().one()








class UserRaw:
    @staticmethod
    async def check_user_raw(session: AsyncSession, username: str | None = None, user_id: int | None = None,
                         register: bool = False):
        filters = []
        values = {}
        if user_id:
            filters.append('id = :user_id')
            values['user_id'] = user_id
        if username:
            filters.append('username = :username')
            values['username'] = username

        add_where = f'WHERE {' AND '.join(filters)}' if filters else ''
        stmt = text(f"SELECT * FROM users {add_where}")
        result = await session.execute(stmt, values)
        res = result.first()
        return await handle_user_result(res,register)

    @staticmethod
    async def delete_user_raw(user_id: int, session: AsyncSession):
        await UserRaw.check_user_raw(session=session, user_id=user_id)
        stmt = text("DELETE FROM users WHERE id = :user_id")
        res = await session.execute(stmt, {"user_id": user_id})
        await session.commit()
        return {"message": "User deleted successfully!"}
from typing import Any, Dict, List
from fastapi import HTTPException
from sqlalchemy import text, select, case, func, update, null, delete, asc, desc, and_, insert
from sqlalchemy.ext.asyncio import AsyncSession
from models import Todo as TodoModel, User as UserModel
from todo.schema import TodosParams, TodosResponse, TodoResponse, TodoUpdate, Todo
from user.crud import UserOrm


class TodoOrm:

    @staticmethod
    async def create_todo_orm(todo: Todo, session: AsyncSession):
        await UserOrm.check_user_orm(user_id=todo.user_id, session=session)
        print(session,todo)
        stmt = insert(TodoModel).values(title=todo.title, description=todo.description, user_id=todo.user_id).returning(TodoModel)
        query = await session.execute(stmt)
        result = query.scalars().first()
        await session.commit()
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to create todo")
    @staticmethod
    async def get_todo_by_id_orm(session: AsyncSession, id: int = None, ids: List[int] = None):
        if ids:
            stmt = select(TodoModel).where(TodoModel.id.in_(ids))
            query = await session.execute(stmt)
            result = query.scalars().all()
            if len(ids) != len(result):
                raise HTTPException(status_code=404, detail="Todos not found")
            return [TodoResponse.model_validate(r) for r in result]
        stmt = select(TodoModel).filter_by(id=id)
        query = await session.execute(stmt)
        result = query.scalars().first()
        if result:
            dict_result = TodoResponse.model_validate(result)
            return dict_result
        raise HTTPException(status_code=404, detail="Todo not found")

    @staticmethod
    async def update_todos_with_params_orm(ids: list, completed: bool, session: AsyncSession):
        completed_at_value = func.now() if completed else None
        stmt = (update(TodoModel)
                .where(TodoModel.id.in_(ids))
                .values(completed=completed, completed_at=completed_at_value))
        query = await session.execute(stmt)
        await session.commit()
        return {"message": "Todos updated successfully!"}


    @staticmethod
    async def update_todo_orm(id:int,todo:TodoUpdate,session:AsyncSession):
        check_todo = await TodoOrm.get_todo_by_id_orm(id=id,session=session)
        stmt = (update(TodoModel)
                .where(TodoModel.id == id)
                .values(title = todo.title,description=todo.description,completed=todo.completed,user_id=todo.user_id)
                )
        query = await session.execute(stmt)
        await session.commit()

    @staticmethod
    async def delete_todo_orm(session: AsyncSession, id: int):
        check_todo = await TodoOrm.get_todo_by_id_orm(id=id, session=session)
        stmt = delete(TodoModel).where(TodoModel.id == id)
        query = await session.execute(stmt)
        await session.commit()
        return

    @staticmethod
    async def get_todos_with_params_orm(session: AsyncSession, todos: TodosParams):
        func_order = asc
        filters = []
        if todos.sort_by.startswith('-'):
            todos.sort_by = str(todos.sort_by[1:])
            func_order = desc
        if todos.completed is not None:
            filters.append(TodoModel.completed == todos.completed)
        if todos.title_contains is not None:
            filters.append(TodoModel.title.ilike(f'%{todos.title_contains}%'))
        if todos.created_after is not None:
            filters.append(TodoModel.created_at >= todos.created_after)
        if todos.created_before is not None:
            filters.append(TodoModel.created_at <= todos.created_before)
        stmt = select(TodoModel).where(and_(*filters)).order_by(func_order(todos.sort_by)).limit(todos.limit).offset(
            todos.offset)
        query = await session.execute(stmt)
        result = query.scalars().all()
        if result:
            dicts = [TodoResponse.model_validate(r) for r in result]
            lists = TodosResponse(todos=dicts)
            return lists
        return []


class TodoRaw:

    @staticmethod
    async def create_todo_raw(todo: Todo, session: AsyncSession):
        await UserOrm.check_user_orm(todo.user_id, session)

        stmt = text(
            "INSERT INTO todos (title, description, user_id) VALUES (:title, :description, :user_id) RETURNING *")
        result = await session.execute(stmt, {
            "title": todo.title,
            "description": todo.description,
            'user_id': todo.user_id
        })
        await session.commit()
        row = result.first()
        if row:
            columns = result.keys()
            res = dict(zip(columns, row))
            return res
        else:
            raise HTTPException(status_code=500, detail="Failed to create todo")
    @staticmethod
    async def get_todo_by_id_raw(session:AsyncSession,id:int=None,ids:List[int]=None):
        if ids:
            stmt = text("SELECT * FROM todos WHERE id = ANY(:ids)")
            res = await session.execute(stmt, {"ids": ids})
            result = res.all()
            if len(ids) != len(result):
                raise HTTPException(status_code=404, detail="Todos not found")
            return [TodoResponse(**(r._asdict())) for r in result]
        stmt = text("SELECT * FROM todos WHERE id = :id")
        res = await session.execute(stmt, {"id": id})
        result = res.first()
        if result:
            dict_result = dict(zip(res.keys(), result))
            return dict_result
        raise HTTPException(status_code=404, detail="Todo not found")


    @staticmethod
    async def update_todo(id: int, todo: TodoUpdate, session: AsyncSession):
        await TodoOrm.get_todo_by_id_orm(id=id, session=session)
        # await get_user_by_id(todo.user_id, session)
        stmt = text(
            "UPDATE todos SET title = :title , description = :description , completed = :completed,user_id = :user_id WHERE id = :id")
        res = await session.execute(stmt, {
            'title': todo.title,
            'description': todo.description,
            'completed': todo.completed,
            'id': id,
            'user_id': todo.user_id})
        await session.commit()
        return {'Message':'Todo success updated'}
    @staticmethod
    async def update_todos_with_params_raw(ids:list,completed:bool,session:AsyncSession):
        stmt = text("UPDATE todos SET completed =:completed ,completed_at = CASE WHEN completed THEN now() ELSE NULL END WHERE id = ANY(:ids)")

        res = await session.execute(stmt,{'ids':ids,'completed':completed})
        await session.commit()
        return {"message": "Todos updated successfully!"}

    @staticmethod
    async def delete_todo_raw(session:AsyncSession,id:int):
        check_todo = await TodoRaw.get_todo_by_id_raw(id=id,session=session)
        stmt = text("DELETE FROM todos WHERE id = :id")
        res = await session.execute(stmt,{'id':id})
        await session.commit()
        return

    @staticmethod
    async def get_todos_with_params_raw(session:AsyncSession,todos:TodosParams):
        order = 'ASC'
        filters = []
        values: Dict[str, Any] = {'limit': todos.limit, 'offset': todos.offset}
        if todos.sort_by.startswith('-'):
            todos.sort_by = str(todos.sort_by[1:])
            order = 'DESC'
        if todos.completed is not None:
            filters.append("completed = :completed")
            values['completed'] = todos.completed
        if todos.title_contains is not None:
            filters.append("title ILIKE :title_contains")
            values['title_contains'] = f"%{todos.title_contains}%"
        if todos.created_after is not None :
            filters.append("created_at >= :created_after")
            values['created_after'] = todos.created_after
        if todos.created_before is not None:
            filters.append("created_at <= :created_before")
            values['created_before'] = todos.created_before

        add_where = f'WHERE {" AND ".join(filters)}'if filters else ''

        stmt = text(f"SELECT * FROM todos {add_where} ORDER BY {todos.sort_by} {order} LIMIT :limit OFFSET :offset")
        res = await session.execute(stmt,values)
        result = res.all()
        if result:
            print(result)
            dicts= [TodoResponse(**(r._asdict())) for r in result]
            lists = TodosResponse(todos=dicts)
            return lists
        return []


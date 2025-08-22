from typing import List
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from todo.analytics import get_analysis_from_todos
from todo.crud import TodoOrm
from todo.schema import TodoUpdate, Todo, TodosParams
from user.crud import UserOrm

router = APIRouter(tags=["Todo"], prefix="/todos")

@router.post('/todo')
async def create_todo(todo: Todo, session: AsyncSession = Depends(get_session)):
    result = await TodoOrm.create_todo_orm(todo=todo,session=session)
    return {"message": "Todo created successfully", 'result': result}



@router.get('/todos')
async def get_todos(todos:TodosParams = Query(...),session:AsyncSession = Depends(get_session)):
    result = await TodoOrm.get_todos_with_params_orm(session,todos)
    return result
@router.get('/todo/{id}')
async def get_todo(id:int,session:AsyncSession = Depends(get_session)):
    result = await TodoOrm.get_todo_by_id_orm(id=id,session=session)
    return result

@router.get('/analytics/')
async def get_analytics(timezone: str = Query('Europe/Samara'),session:AsyncSession = Depends(get_session)):
    res = await get_analysis_from_todos(timezone,session)
    return res


@router.put('/todo/{id}')
async def update_todo(id:int,todo:TodoUpdate,session:AsyncSession=Depends(get_session)):
    await TodoOrm.update_todo_orm(id=id,todo=todo,session=session)
    return {"message": "Todo updated successfully!"}

@router.patch('/todos/')
async def update_todos(ids:List[int] | int = Query(),completed:bool = Query(True),session:AsyncSession=Depends(get_session)):
    # rq = await TodoOrm.get_todo_by_id_orm(ids=ids,session=session)
    res = await TodoOrm.update_todos_with_params_orm(ids=ids,completed=completed,session=session)
    return {'message':'Todos successfully updated'}


@router.delete('/todo/{id}')
async def delete_todo_by_id(id:int,session:AsyncSession=Depends(get_session)):
    await TodoOrm.delete_todo_orm(id=id,session=session)
    return {"message": "Todo deleted successfully!"}
from datetime import datetime,date
from decimal import Decimal
from enum import Enum
from typing import List, Union, Literal, Dict

from fastapi import Query, HTTPException
from pydantic import BaseModel, field_validator, ConfigDict


class SortParams(str,Enum):
    title = "title"
    description = "description"
    created_at = "created_at"

    @classmethod
    def get_params(cls):
        params = []
        for param in cls:
            params.append(f"-{param.value}")
            params.append(param.value)
        return params


class AnalyticTodoResponse(BaseModel):
    total:int
    completed_count:int
    not_completed_count:int
    avg_completed_time:float
    weekday_distribution :Dict[str,int]

@field_validator("avg_completed_time")
def validate_avg_completed_time(cls,value):
    return float(value)

class TodoUpdate(BaseModel):
    title:str
    description:str
    completed:bool
    user_id:int

class Todo(BaseModel):
    title: str
    description:str
    user_id:int
class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id: int
    completed: bool
    user_id:int
    created_at:datetime
    updated_at:datetime
    completed_at:datetime | None
    model_config = ConfigDict(from_attributes=True)
class TodosResponse(BaseModel):
    todos: List[TodoResponse]

class TodosParams(BaseModel):
    limit: int = Query(default=10, le=100)
    offset: int = Query(default=0)
    sort_by : str = Query(default='title')
    completed:bool | None = Query(default=None)
    created_before:str | None = Query(default=None)
    created_after:str | None = Query(default=None)
    title_contains:str | None = Query(default=None)
    @field_validator("sort_by")
    def validate_sort_by(cls,value):
        if value not in SortParams.get_params():
            raise HTTPException(status_code=403,detail="Неверный параметр сортировки")
        return value

    @classmethod
    def validate_time(cls,value):
        try:
            checked_value = datetime.fromisoformat(value)
            return checked_value
        except  ValueError:
            raise HTTPException(status_code=403,detail="Неверный формат даты")

    @field_validator("created_before")
    def validate_created_before(cls,value):
        if value:
            return cls.validate_time(value)
        return None

    @field_validator("created_after")
    def validate_created_after(cls, value):
        if value:
            return cls.validate_time(value)
        return None


# c = TodosParams(limit=10,offset=0,sort_by='title',completed=True,created_before="2024-12-23",created_after=None,title_contains=None)


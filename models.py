from pydantic import BaseModel,Field
from typing import Optional


class TaskCreate(BaseModel):
    title:str=Field(min_length=1)
    description: Optional[str]=None
    priority: int =Field(ge=1,le=3)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]=None
    priority: int
    completed: bool
    project_id: int

class TaskUpdate(BaseModel):
    title: str
    description:Optional[str]=None
    priority:int=Field(ge=1,le=3)
    completed: bool

class TaskPatch(BaseModel):
    title: Optional[str]=None
    description:Optional[str]=None
    priority:Optional[int]=Field(default=None,ge=1,le=3)
    completed:Optional[bool]=None

class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]

class TaskStatsResponse(BaseModel):
    total:int
    completed:int
    pending:int
    high_priority:int

class ProjectCreate(BaseModel):
    name:str=Field(min_length=1)

class ProjectResponse(BaseModel):
    id:int
    name:str
    user_id:int

class UserCreate(BaseModel):
    username:str=Field(min_length=3)
    email:str
    password:str=Field(min_length=8)

class UserResponse(BaseModel):
    id:int
    username:str
    email:str

class ProjectDashboardResponse(BaseModel):
    project_id:int
    project_name:str
    total_tasks:int
    completed_tasks:int
    pending_tasks:int
    high_priority_tasks:int
    
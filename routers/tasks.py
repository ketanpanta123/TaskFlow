from fastapi import APIRouter,Depends,Query,HTTPException
from typing import Optional
from dependencies import get_current_user,pagination
from data import tasks
from models import TaskCreate,TaskResponse,TaskUpdate,TaskPatch,TaskListResponse,TaskStatsResponse
from services.task_service import create_task,update_task,patch_task,delete_task,get_tasks,get_task_stats
from sqlalchemy import select,func,case
from sqlalchemy.orm import Session
from db_models import Task,Project
from database import get_db

router=APIRouter(prefix="/tasks",tags=["tasks"])

@router.get("/stats",response_model=TaskStatsResponse)
def get_task_stats_endpoint(user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(
        func.count(Task.id).label("total"),
        func.count(case((Task.completed==True,1))).label("completed"),
        func.count(case((Task.completed==False,1))).label("pending"),
        func.count(case((Task.priority==3,1))).label("high_priority")
    ).join(Project).where(Project.user_id==user.id)

    result=db.execute(statement)
    stats=result.one()

    return{
        "total":stats.total,
        "completed":stats.completed,
        "pending":stats.pending,
        "high_priority":stats.high_priority
    }

@router.get("/{task_id}",response_model=TaskResponse)
def get_task_by_task_id(task_id:int,user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(Task).join(Project).where(Task.id==task_id,Project.user_id==user.id)
    result=db.execute(statement)
    task=result.scalar_one_or_none()
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        ) 
    return task  


@router.put("/{task_id}",response_model=TaskResponse)
def task_update_endpoint(task_id:int,task_data:TaskUpdate,user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(Task).join(Project).where(
        Task.id==task_id,
        Project.user_id==user.id
    )
    result=db.execute(statement)
    task=result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="task not found"
        )
    task.title=task_data.title
    task.description=task_data.description
    task.priority=task_data.priority
    task.completed=task_data.completed

    db.commit()
    db.refresh(task)

    return task
    

@router.patch("/{task_id}",response_model=TaskResponse)
def patch_task_endpoint(task_id:int,task_data: TaskPatch,user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(Task).join(Project).where(Task.id==task_id,Project.user_id==user.id)
    result=db.execute(statement)
    task=result.scalar_one_or_none()
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="task not found"
        )

    update_data=task_data.model_dump(exclude_unset=True)

    for field,value in update_data.items():
        setattr(task,field,value)
    db.commit()
    db.refresh(task)

    return task    

@router.delete("/{task_id}")
def delete_task_endpoint(task_id:int,user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(Task).join(Project).where(Task.id==task_id,Project.user_id==user.id)
    result=db.execute(statement)
    task=result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    db.delete(task)
    db.commit()
    return{
        "message":"Task deleted successfully"
    }

@router.get("/",response_model=TaskListResponse)
def get_tasks_endpoint(
    priority: Optional[int]=None,
    completed: Optional[bool]=None,
    pagination=Depends(pagination),
    sort: Optional[str]=None,
    user=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    statement=select(Task).join(Project).where(
        Project.user_id==user.id
    )
    if priority is not None:
        statement=statement.where(
            Task.priority==priority
        )
    if completed is not None:
        statement=statement.where(
            Task.completed==completed
        )
    sort_fields={
        "id":Task.id,
        "title":Task.title,
        "description":Task.description,
        "priority":Task.priority,
        "completed":Task.completed
    }

    if sort is not None:
        descending=sort.startswith("-")
        field_name=sort[1:] if descending else sort

        if field_name not in sort_fields:
            raise HTTPException(
                status_code=400,
                detail="Invalid sort field"
            )
        field=sort_fields[field_name]

        if descending:
            statement=statement.order_by(field.desc())
        else:
            statement=statement.order_by(field.asc())
    skip=pagination["skip"]
    limit=pagination["limit"]

    statement=statement.offset(skip).limit(limit)

    results=db.execute(statement)
    tasks=results.scalars().all()

    return {"tasks":tasks}


from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select,func,case


from dependencies import get_current_user,get_current_project
from database import get_db
from db_models import Project,Task
from models import ProjectCreate,ProjectResponse,TaskCreate,TaskResponse,TaskListResponse,ProjectDashboardResponse

router=APIRouter(prefix="/projects",tags=["projects"])

@router.post("/",response_model=ProjectResponse,status_code=201)
def create_project(project:ProjectCreate,user=Depends(get_current_user),db:Session=Depends(get_db)):
    new_project=Project(
        name=project.name,
        user_id=user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project

@router.get("/",response_model=list[ProjectResponse])
def get_projects(user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(Project).where(Project.user_id==user.id)
    results=db.execute(statement)
    projects=results.scalars().all()
    return projects



@router.post("/{project_id}/tasks/",response_model=TaskResponse,status_code=201)
def create_task(task:TaskCreate,project=Depends(get_current_project),db:Session=Depends(get_db)):
    new_task=Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        completed=False,
        project_id=project.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@router.get("/{project_id}/tasks/",response_model=TaskListResponse)
def get_project_tasks(project=Depends(get_current_project),db:Session=Depends(get_db)):
    statement=select(Task).where(Task.project_id==project.id)
    results=db.execute(statement)
    tasks=results.scalars().all()

    return {
        "tasks":tasks
    }

@router.get("/{project_id}/dashboard",response_model=ProjectDashboardResponse)
def het_project_dashboard(project=Depends(get_current_project),db:Session=Depends(get_db)):
    statement=select(
        func.count(Task.id).label("total_tasks"),
        func.count(case((Task.completed==True,1))).label("completed_tasks"),
        func.count(case((Task.completed==False,1))).label("pending_tasks"),
        func.count(case((Task.priority==3,1))).label("high_priority_tasks")
    ).where(Task.project_id==project.id)

    result=db.execute(statement)
    stats=result.one()

    return {
        "project_id":project.id,
        "project_name":project.name,
        "total_tasks":stats.total_tasks,
        "completed_tasks":stats.completed_tasks,
        "pending_tasks":stats.pending_tasks,
        "high_priority_task":stats.high_priority_tasks
    }


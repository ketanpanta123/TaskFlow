from models import TaskCreate,TaskUpdate,TaskPatch
import data

def create_task(task: TaskCreate,user: dict):
    new_task={
        "id":data.next_task_id,
        "title": task.title,
        "description":task.description,
        "priority":task.priority,
        "completed":False,
        "user_id":user["id"]
    }

    data.next_task_id+=1
    data.tasks.append(new_task)

    return new_task

def update_task(task:dict, task_data: TaskUpdate):
    task["title"]=task_data.title
    task["description"]=task_data.description
    task["priority"]=task_data.priority
    task["completed"]=task_data.completed

    return task

def patch_task(task:dict, task_data: TaskPatch):
    updates=task_data.model_dump(exclude_unset=True)

    task.update(updates)

    return task

def delete_task(task:dict):
    data.tasks.remove(task)

    return {"message":"Task deleted successfully"}


def get_tasks(
        user_id:int,
        priority: int | None = None,
        completed: bool | None=None,
        skip: int=0,
        limit:int=10,
        sort: str|None=None 
):
    filtered_tasks=[
        task for task in data.tasks
        if task["user_id"]==user_id
    ]
    if priority is not None:
        filtered_tasks=[
            task for task in filtered_tasks
            if task["priority"]==priority
        ]
    if completed is not None:
        filtered_tasks=[
            task for task in filtered_tasks
            if task["completed"]==completed
        ]
    if sort is not None:
        allowed_sort=[
            "id",
            "title",
            "description",
            "priority",
            "completed"
        ]
        descending=sort.startswith("-")
        sort_field=sort.lstrip("-")

        if sort_field not in allowed_sort:
            raise ValueError("invalid sort field")

        filtered_tasks=sorted(filtered_tasks,key=lambda task:task[sort_field], reverse=descending) 

    filtered_tasks=filtered_tasks[skip:skip+limit]

    return filtered_tasks


def get_task_stats(user:dict):
    user_tasks=[
        task for task in data.tasks
        if task["user_id"]==user["id"]
    ]
    total=len(user_tasks)
    completed=0
    pending=0
    high_priority=0
    for task in user_tasks:
        if task["completed"]==True:
            completed+=1
        else:
            pending+=1
        if task["priority"]==3:
            high_priority+=1
    stats={
        "total":total,
        "completed":completed,
        "pending":pending,
        "high_priority":high_priority
    }

    return stats
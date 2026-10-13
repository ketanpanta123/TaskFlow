from fastapi import FastAPI



from routers.tasks import router as task_router
from routers.users import router as user_router
from routers.projects import router as project_router
from routers.auth import router as auth_router




app=FastAPI()
app.include_router(task_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(auth_router)



@app.get("/")
def home():
    return {"message": "TaskFlow API"}


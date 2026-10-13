from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from fastapi import Depends,HTTPException,Query

from database import get_db
from db_models import Project,User
from security import JWT_SECRET_KEY,JWT_ALGORITHM

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")




def get_current_user(token =Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )


        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    statement=select(User).where(User.id==int(user_id))
    result=db.execute(statement)
    user=result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    return user

    

    


def pagination(skip:int=Query(default=0,ge=0),limit: int=Query(default=10,ge=1,le=100)):
    return {
        "skip":skip,
        "limit":limit,
    }

def get_current_project(project_id:int,user=Depends(get_current_user),db:Session=Depends(get_db)):
    statement=select(Project).where(
        Project.id==project_id,
        Project.user_id==user.id
    )
    result=db.execute(statement)
    project=result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    return project
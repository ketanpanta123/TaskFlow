from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from db_models import User
from security import verify_password,create_access_token
from dependencies import get_current_user

router=APIRouter(prefix="/auth",tags=["authentication"])

@router.post("/login")
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    statement=select(User).where(User.email==form_data.username)
    result=db.execute(statement)

    user=result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    if not verify_password(form_data.password,user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    access_token=create_access_token(user.id)

    return{
         "access_token":access_token,
         "token_type":"bearer"
         }

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return{
        "id":user.id,
        "username":user.username,
        "email":user.email
    }


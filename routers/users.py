from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from db_models import User
from models import UserCreate,UserResponse
from security import hash_password

router=APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register",response_model=UserResponse,status_code=201)
def register_user(
    user_data:UserCreate,
    db:Session=Depends(get_db)
):
    hashed_password=hash_password(user_data.password)

    new_user=User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    return new_user
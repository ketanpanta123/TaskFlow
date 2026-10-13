from database import engine
from sqlalchemy.orm import Session
from db_models import User

with Session(engine) as session:
    user = session.get(User, 1)

    print(user.username)
    print(user.email)
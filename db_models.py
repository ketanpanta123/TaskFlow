from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship
from sqlalchemy import String,ForeignKey

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True)
    username:Mapped[str]=mapped_column(String,nullable=False)
    email:Mapped[str]=mapped_column(String,nullable=False,unique=True)
    password_hash:Mapped[str]=mapped_column(String,nullable=False)
    projects:Mapped[list["Project"]]=relationship(back_populates="user")

class Project(Base):
    __tablename__="projects"

    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String,nullable=False)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    tasks:Mapped[list["Task"]]=relationship(back_populates="project")
    user:Mapped["User"]=relationship(back_populates="projects")

class Task(Base):
    __tablename__="tasks"

    id:Mapped[int]=mapped_column(primary_key=True)
    title:Mapped[str]=mapped_column(String,nullable=False)
    description:Mapped[str|None]=mapped_column(String,nullable=True)
    priority:Mapped[int]
    completed:Mapped[bool]=mapped_column(default=False)
    project_id:Mapped[int]=mapped_column(ForeignKey("projects.id",ondelete="CASCADE"),nullable=False)
    project:Mapped["Project"]=relationship(back_populates="tasks")



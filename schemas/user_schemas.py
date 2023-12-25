from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    
class UserCreate(UserBase):
    password: str
    email: str = None
    
class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: str | None = None

class User(UserBase):
    email: str
    create_time: datetime
    model_config = {"from_attributes": True}

class UserWithoutTasks(UserBase):
    create_time: datetime

class UserLogin(UserBase):
    password: str
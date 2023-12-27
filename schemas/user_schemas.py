from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    
class UserCreate(UserBase):
    password: str
    email: EmailStr
    
class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: EmailStr | None = None

class User(UserBase):
    email: str
    model_config = {"from_attributes": True}

class UserLogin(UserBase):
    password: str
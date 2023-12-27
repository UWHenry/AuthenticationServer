from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from database import DatabaseDependency
from models.user import User as DB_User
from schemas.user_schemas import User, UserCreate, UserUpdate
from schemas.util_schemas import ExceptionMessage
from utils.crud import UserCRUD
from utils.jwt import TokenDependency, get_jwt_username


user_router = APIRouter(
    prefix="/users",
    tags=["uesr"]
)

async def get_current_user(token: TokenDependency, db: DatabaseDependency) -> User:
    username = get_jwt_username(token)
    user = await UserCRUD.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return user
JWT_USER_DEPENDENCY = Annotated[DB_User, Depends(get_current_user)]

@user_router.get("/me", responses={401: {"model": ExceptionMessage}})
async def get_user(user: JWT_USER_DEPENDENCY) -> User:
    return user

@user_router.post("", status_code= 201, responses={409: {"model": ExceptionMessage}})
async def create_user(user: UserCreate, db: DatabaseDependency) -> User:
    try:
        return await UserCRUD.create_user(db, user)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username Already Exists")

@user_router.put("", responses = {401: {"model": ExceptionMessage}, 409: {"model": ExceptionMessage}})
async def update_user(updates: UserUpdate, user: JWT_USER_DEPENDENCY, db: DatabaseDependency) -> User:
    try:
        result = await UserCRUD.update_user(db, user.id, updates)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username Already Exists")
    return result

@user_router.delete("", status_code=204)
async def delete_user(user: JWT_USER_DEPENDENCY, db: DatabaseDependency) -> None:
    await UserCRUD.delete_user_by_username(db, user.username)
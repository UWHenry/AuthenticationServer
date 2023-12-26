from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from jose import JWTError

from database import DatabaseDependency
from schemas.user_schemas import User, UserCreate, UserUpdate
from schemas.util_schemas import ExceptionMessage
from utils.crud import UserCRUD
from utils.jwt import TokenDependency, decode_token


user_router = APIRouter(
    prefix="/users",
    tags=["uesr"]
)

async def get_current_user(token: TokenDependency, db: DatabaseDependency) -> User:
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    username = payload.get("sub")
    user = await UserCRUD.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return user

@user_router.get("/me", responses={401: {"model": ExceptionMessage}})
async def read(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user

@user_router.post("", status_code= 201, responses={409: {"model": ExceptionMessage}})
async def create(user: UserCreate, db: DatabaseDependency) -> User:
    try:
        return await UserCRUD.create_user(db, user)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username Already Exists")

@user_router.put("", responses = {401: {"model": ExceptionMessage}, 409: {"model": ExceptionMessage}})
async def update(updates: UserUpdate, user: Annotated[User, Depends(get_current_user)], db: DatabaseDependency) -> User:
    try:
        result = await UserCRUD.update_user(db, user.id, updates)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Username Already Exists")
    return result

@user_router.delete("", status_code=204)
async def delete(user: Annotated[User, Depends(get_current_user)], db: DatabaseDependency) -> None:
    await UserCRUD.delete_user_by_username(db, user.username)
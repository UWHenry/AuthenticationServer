from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from database import DatabaseDependency
from models.user import User
from schemas.token_schemas import JWTToken, TokenCreate
from schemas.util_schemas import ExceptionMessage
from utils.crud import UserCRUD, TokenCRUD
from utils.password_utils import verify_password
from utils.jwt import create_access_token, create_refresh_token


auth_router = APIRouter(
    prefix="",
    tags=["authentication"]
)

async def authenticate_user(username: str, password: str, db: AsyncSession) -> User | None:
    user = await UserCRUD.get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

@auth_router.post("/token", responses={401: {"model": ExceptionMessage}})
async def generate_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: DatabaseDependency
) -> JWTToken:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token()
    token = TokenCreate(
        access_token=access_token, 
        refresh_token=refresh_token, 
        user_id=user.id
    )
    return await TokenCRUD.create_token(db, token)
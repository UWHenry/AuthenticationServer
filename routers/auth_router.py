from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database import DatabaseDependency
from models.user import User
from schemas.token_schemas import JWTToken, TokenCreate, RefreshToken
from schemas.util_schemas import ExceptionMessage
from utils.crud import UserCRUD, TokenCRUD
from utils.password_utils import verify_password
from utils.jwt import create_access_token, create_refresh_token, TokenDependency
from routers.user_router import get_current_user

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
async def generate_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: DatabaseDependency
) -> JWTToken:
    user = await authenticate_user(form_data.username, form_data.password, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    access_token = create_access_token(user.username)
    token = TokenCreate(
        token=access_token, 
        user_id=user.id
    )
    return await TokenCRUD.create_access_token(db, token)

@auth_router.post("/refresh_token", responses={401: {"model": ExceptionMessage}})
async def generate_refresh_token(token: TokenDependency, db: DatabaseDependency) -> RefreshToken:
    user = await get_current_user(token, db)
    refresh_token = create_refresh_token()
    token = TokenCreate(
        token=refresh_token,
        user_id=user.id
    )
    try:
        db_token = await TokenCRUD.create_refresh_token(db, token)
    except IntegrityError:
        await db.rollback()
        db_token = await TokenCRUD.update_refresh_token(db, token)
    return db_token

@auth_router.post("/refresh", responses={401: {"model": ExceptionMessage}})
async def generate_access_token_with_refresh_token(refresh_token: str, token: TokenDependency, db: DatabaseDependency) -> JWTToken:
    user = await get_current_user(token, db)
    db_token = await TokenCRUD.get_refresh_token_by_userid(db, user.id)
    if db_token is None or db_token.refresh_token != refresh_token:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    access_token = create_access_token(user.username)
    token = TokenCreate(
        token=access_token, 
        user_id=user.id
    )
    return await TokenCRUD.create_access_token(db, token)
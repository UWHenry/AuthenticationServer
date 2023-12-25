from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.user import User
from models.token import Token
from schemas.user_schemas import UserCreate, UserUpdate
from schemas.token_schemas import TokenCreate
from utils.password_utils import get_password_hash
from utils.jwt import REFRESH_TOKEN_EXPIRE_MINUTES

class UserCRUD:
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        results = await db.execute(select(User).filter(User.username == username))
        return results.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, id: int) -> User | None:
        results = await db.execute(select(User).filter(User.id == id))
        return results.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, password_hash=hashed_password, email=user.email)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def delete_user_by_username(db: AsyncSession, username: str) -> int:
        result = await db.execute(delete(User).where(User.username == username))
        await db.commit()
        return result.rowcount

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> User | None:
        db_user = await UserCRUD.get_user_by_id(db, user_id)
        if db_user is not None:
            if user.username is not None:
                db_user.username = user.username
            if user.password is not None:
                db_user.password_hash = get_password_hash(user.password)
            if user.email is not None:
                db_user.email = user.email
            await db.commit()
            await db.refresh(db_user)
        return db_user

class TokenCRUD:
    @staticmethod
    async def create_token(db: AsyncSession, token: TokenCreate) -> Token:
        db_token = Token(access_token=token.access_token, refresh_token=token.refresh_token, user_id=token.user_id)
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token
    
    @staticmethod
    async def delete_expired_tokens(db: AsyncSession, refresh_token_alive_time: int = None) -> int:
        if refresh_token_alive_time is None:
            refresh_token_alive_time = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        earliest_token_alive_time  = datetime.utcnow() - refresh_token_alive_time
        result = await db.execute(delete(Token).where(Token.create_time < earliest_token_alive_time))
        await db.commit()
        return result.rowcount
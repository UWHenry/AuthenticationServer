from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models.user import User
from models.access_token import AccessToken
from models.refresh_token import RefreshToken
from schemas.user_schemas import UserCreate, UserUpdate
from schemas.token_schemas import TokenCreate
from utils.password_utils import get_password_hash
from utils.jwt import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

class UserCRUD:
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
        results = await db.execute(select(User).filter(User.username == username))
        return results.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        results = await db.execute(select(User).filter(User.id == user_id))
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
    async def create_access_token(db: AsyncSession, token: TokenCreate) -> AccessToken:
        db_token = AccessToken(
            access_token=token.token, 
            expiration_time=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            user_id=token.user_id
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token
    
    @staticmethod
    async def get_refresh_token_by_userid(db: AsyncSession, user_id: str) -> RefreshToken | None:
        results = await db.execute(select(RefreshToken).filter(RefreshToken.user_id == user_id))
        return results.scalars().first()
    
    @staticmethod
    async def create_refresh_token(db: AsyncSession, token: TokenCreate) -> RefreshToken:
        db_token = RefreshToken(
            user_id=token.user_id,
            refresh_token=token.token,
            expiration_time=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        return db_token

    @staticmethod
    async def update_refresh_token(db: AsyncSession, token: TokenCreate) -> RefreshToken | None:
        db_token = await TokenCRUD.get_refresh_token_by_userid(db, token.user_id)
        if db_token is not None:
            db_token.refresh_token = token.token
            db_token.expiration_time = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            await db.commit()
            await db.refresh(db_token)
        return db_token
    
    
    @staticmethod
    async def delete_expired_access_tokens(db: AsyncSession) -> int:
        result = await db.execute(delete(AccessToken).where(AccessToken.expiration_time < datetime.utcnow()))
        await db.commit()
        return result.rowcount
    
    @staticmethod
    async def delete_expired_refresh_tokens(db: AsyncSession) -> int:
        result = await db.execute(delete(RefreshToken).where(RefreshToken.expiration_time < datetime.utcnow()))
        await db.commit()
        return result.rowcount
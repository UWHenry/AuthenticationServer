import os
from typing import Annotated

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

DatabaseDependency = Annotated[AsyncSession, Depends(get_db)]
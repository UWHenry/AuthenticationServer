from dotenv import load_dotenv
load_dotenv(override=True)

import asyncio
import os

from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from database import init_db, SessionLocal
from routers.user_router import user_router
from routers.auth_router import auth_router
from utils.crud import TokenCRUD


async def periodic_token_cleanup(db: AsyncSession):
    token_cleanup_interval = os.environ.get("TOKEN_CLEANUP_MINUTES", 60)
    while True:
        await TokenCRUD.delete_expired_tokens(db)
        await asyncio.sleep(token_cleanup_interval * 60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    db = SessionLocal()
    task = asyncio.create_task(periodic_token_cleanup(db))
    yield
    task.cancel()
    await db.close()
        
app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(auth_router)
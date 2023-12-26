import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from main import app, lifespan
from database import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///test.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def mock_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[lifespan] = None

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
        
@pytest.fixture(params=['asyncio'])
def anyio_backend(request):
    return request.param
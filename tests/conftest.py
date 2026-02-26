import random
from datetime import UTC, datetime
from typing import Optional
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config.settings import settings
from app.domain.entities.task import TaskEntity
from app.domain.enums import TaskStatus
from app.domain.repositories import TaskRepositoryInterface
from app.infrastructure.db import Task, get_async_session
from app.infrastructure.db.repositories.task import TaskRepository
from app.main import app
from app.services.task_service import TaskService


@pytest_asyncio.fixture
async def async_engine():
    DATABASE_URL = settings.get_db_url()
    engine = create_async_engine(DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    async with async_engine.connect() as conn:
        trans = await conn.begin()
        async_session_maker = async_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )
        session = async_session_maker()
        yield session
        await session.close()
        await trans.rollback()


@pytest_asyncio.fixture
async def create_task(async_session):
    async def _create(
        title: str,
        status: Optional[TaskStatus] = TaskStatus.NEW,
        result: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> Task:
        task = Task(title=title, status=status, result=result)
        if created_at:
            task.created_at = created_at
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)
        return task

    return _create


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=TaskRepositoryInterface)


@pytest.fixture
def make_task():
    def _create(
        title: str,
        id: Optional[int] = None,
        status: TaskStatus = TaskStatus.NEW,
        result: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> TaskEntity:
        now = datetime.now(UTC)
        return TaskEntity(
            id=id or random.randint(0, 10),
            title=title,
            status=status,
            result=result,
            created_at=created_at or now,
            updated_at=updated_at or now,
        )

    return _create


@pytest_asyncio.fixture
async def service(async_session):
    repo = TaskRepository(async_session)
    service = TaskService(repo)
    yield service


@pytest_asyncio.fixture(autouse=True)
async def override_get_async_session(async_session):
    async def _override():
        yield async_session

    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(request):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

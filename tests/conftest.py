from datetime import datetime
from typing import Optional

import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config.settings import settings
from app.domain.enums import TaskStatus
from app.infrastructure.db import Task


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

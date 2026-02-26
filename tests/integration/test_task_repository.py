from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.domain.enums import TaskStatus
from app.domain.exceptions import TaskNotFound
from app.infrastructure.db import Task
from app.infrastructure.db.repositories.task import TaskRepository


@pytest.mark.asyncio
async def test_create_task_success(async_session):
    task_title = "Test create task"
    repo = TaskRepository(async_session)
    created = await repo.create(title=task_title)

    result = await async_session.execute(select(Task).where(Task.id == created.id))
    task = result.scalar_one_or_none()

    assert task is not None
    assert task.id == created.id
    assert task.title == task_title == created.title
    assert task.status == TaskStatus.NEW == created.status
    assert task.result is None


@pytest.mark.asyncio
async def test_get_task(async_session, create_task):
    task_title = "Test get task"
    created = await create_task(title=task_title)

    repo = TaskRepository(async_session)
    task = await repo.get(created.id)

    assert task is not None
    assert task.id == created.id
    assert task.title == task_title == created.title
    assert task.status == TaskStatus.NEW == created.status


@pytest.mark.asyncio
async def test_get_task_not_found(async_session):
    repo = TaskRepository(async_session)

    with pytest.raises(TaskNotFound):
        await repo.get(999)


@pytest.mark.asyncio
async def test_get_task_return_none(async_session):
    repo = TaskRepository(async_session)

    result = await repo.get(999, return_none=True)

    assert result is None


@pytest.mark.asyncio
async def test_update_status(async_session, create_task):
    task_title = "Test update status"
    task = await create_task(title=task_title)

    repo = TaskRepository(async_session)
    updated = await repo.update(task.id, status=TaskStatus.DONE)

    assert updated.id == task.id
    assert updated.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_update_status_not_found(async_session):
    repo = TaskRepository(async_session)

    with pytest.raises(TaskNotFound):
        await repo.update(999, status=TaskStatus.DONE)


@pytest.mark.asyncio
async def test_get_many_with_status_filter(async_session, create_task):
    repo = TaskRepository(async_session)
    # На случай если в БД уже есть записи, так как используем основную
    exists_tasks = await repo.get_many(status=TaskStatus.NEW)

    task_title = "Test get many"
    await create_task(title=task_title, status=TaskStatus.NEW)
    await create_task(title=task_title, status=TaskStatus.NEW)
    await create_task(title=task_title, status=TaskStatus.DONE)

    tasks = await repo.get_many(status=TaskStatus.NEW)

    assert len(tasks) - len(exists_tasks) == 2
    assert all(task.status == TaskStatus.NEW for task in tasks)


@pytest.mark.asyncio
async def test_get_many_pagination(async_session, create_task):
    repo = TaskRepository(async_session)
    exists_tasks = await repo.get_many()
    base_time = datetime.now(UTC)

    for i in range(5):
        await create_task(
            title=f"Test get many {i}", status=TaskStatus.PROCESSING, created_at=base_time + timedelta(microseconds=i)
        )

    tasks = await repo.get_many(limit=2, offset=len(exists_tasks))

    assert len(tasks) == 2
    assert tasks[0].id < tasks[1].id
    assert tasks[0].created_at < tasks[1].created_at

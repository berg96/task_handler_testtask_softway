from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.domain.enums import TaskStatus
from app.domain.exceptions import InvalidTaskStatusTransition, TaskNotFound
from app.infrastructure.db import Task


@pytest.mark.asyncio
async def test_create_task_success(service, async_session):
    task_title = "Test create task"
    created = await service.create_task(title=task_title)

    result = await async_session.execute(select(Task).where(Task.id == created.id))
    task = result.scalar_one_or_none()

    assert task is not None
    assert task.id == created.id
    assert task.title == task_title == created.title
    assert task.status == TaskStatus.NEW == created.status
    assert task.result is None


@pytest.mark.asyncio
async def test_get_task(service, create_task):
    task_title = "Test get task"
    created = await create_task(title=task_title)

    task = await service.get_task(created.id)

    assert task is not None
    assert task.id == created.id
    assert task.title == task_title == created.title
    assert task.status == TaskStatus.NEW == created.status


@pytest.mark.asyncio
async def test_get_task_not_found(service, async_session):
    with pytest.raises(TaskNotFound):
        await service.get_task(999)


@pytest.mark.asyncio
async def test_update_status(service, create_task):
    task_title = "Test update status"
    task = await create_task(title=task_title)

    updated = await service.update_task_status(task.id, TaskStatus.DONE)

    assert updated.id == task.id
    assert updated.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_update_status_invalid_transition(service, create_task):
    task_title = "Test update status"
    task = await create_task(title=task_title, status=TaskStatus.DONE)

    with pytest.raises(InvalidTaskStatusTransition):
        await service.update_task_status(task.id, TaskStatus.PROCESSING)


@pytest.mark.asyncio
async def test_update_status_not_found(service):
    with pytest.raises(TaskNotFound):
        await service.update_task_status(999, TaskStatus.DONE)


@pytest.mark.asyncio
async def test_get_many_with_status_filter(service, create_task):
    # На случай если в БД уже есть записи, так как используем основную
    exists_tasks = await service.get_many(status=TaskStatus.NEW)

    task_title = "Test get many"
    await create_task(title=task_title, status=TaskStatus.NEW)
    await create_task(title=task_title, status=TaskStatus.NEW)
    await create_task(title=task_title, status=TaskStatus.DONE)

    tasks = await service.get_many(status=TaskStatus.NEW)

    assert len(tasks) - len(exists_tasks) == 2
    assert all(task.status == TaskStatus.NEW for task in tasks)


@pytest.mark.asyncio
async def test_get_many_pagination(service, create_task):
    exists_tasks = await service.get_many()
    base_time = datetime.now(UTC)

    for i in range(5):
        await create_task(
            title=f"Test get many {i}", status=TaskStatus.PROCESSING, created_at=base_time + timedelta(microseconds=i)
        )

    tasks = await service.get_many(limit=2, offset=len(exists_tasks))

    assert len(tasks) == 2
    assert tasks[0].id < tasks[1].id
    assert tasks[0].created_at < tasks[1].created_at

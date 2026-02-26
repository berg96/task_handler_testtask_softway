import pytest

from app.domain.enums import TaskStatus
from app.domain.exceptions import InvalidTaskStatusTransition, TaskNotFound
from app.services.task_service import TaskService
from tests.fakes.fake_task_repo import FakeTaskRepository


@pytest.mark.asyncio
async def test_create_task_success():
    repo = FakeTaskRepository()
    service = TaskService(repo)
    task_title = "Unit test create task"

    task = await service.create_task(title=task_title)

    assert task.id == 1
    assert task.title == task_title
    assert task.status == TaskStatus.NEW


@pytest.mark.asyncio
async def test_create_task_empty_title():
    repo = FakeTaskRepository()
    service = TaskService(repo)
    task_title = ""

    with pytest.raises(ValueError):
        await service.create_task(title=task_title)


@pytest.mark.asyncio
async def test_get_task_success():
    repo = FakeTaskRepository()
    task_title = "Unit test get task"
    created = await repo.create(task_title)
    service = TaskService(repo)

    fetched = await service.get_task(created.id)

    assert fetched.id == created.id
    assert fetched.title == created.title
    assert fetched.created_at == created.created_at


@pytest.mark.asyncio
async def test_get_task_not_found():
    repo = FakeTaskRepository()
    service = TaskService(repo)

    with pytest.raises(TaskNotFound):
        await service.get_task(999)


@pytest.mark.asyncio
async def test_update_status_success():
    repo = FakeTaskRepository()
    task_title = "Unit test update task status"
    created = await repo.create(task_title)
    service = TaskService(repo)

    updated = await service.update_task_status(
        created.id,
        TaskStatus.PROCESSING,
    )

    assert updated.status == TaskStatus.PROCESSING

    fetched = await repo.get(created.id)

    assert fetched.status == TaskStatus.PROCESSING


@pytest.mark.asyncio
async def test_update_status_invalid_transition():
    repo = FakeTaskRepository()
    task_title = "Unit test update task status invalid transition"
    created = await repo.create(title=task_title, status=TaskStatus.DONE)
    service = TaskService(repo)

    with pytest.raises(InvalidTaskStatusTransition):
        await service.update_task_status(created.id, TaskStatus.NEW)


@pytest.mark.asyncio
async def test_update_status_not_found():
    repo = FakeTaskRepository()
    service = TaskService(repo)

    with pytest.raises(TaskNotFound):
        await service.update_task_status(999, TaskStatus.DONE)


@pytest.mark.asyncio
async def test_update_status_calls_repo_methods(mock_repo, make_task):
    service = TaskService(mock_repo)
    task_title = "Unit test update task status calls repo methods"
    mock_repo.get.return_value = make_task(id=1, title=task_title)
    mock_repo.update.return_value = make_task(id=1, title=task_title, status=TaskStatus.PROCESSING)

    await service.update_task_status(1, TaskStatus.PROCESSING)

    mock_repo.get.assert_awaited_once_with(task_id=1)
    mock_repo.update.assert_awaited_once_with(1, status=TaskStatus.PROCESSING)


@pytest.mark.asyncio
async def test_update_status_not_called_on_invalid_transition(mock_repo, make_task):
    service = TaskService(mock_repo)
    task_title = "Unit test update task status not called on invalid transition"
    mock_repo.get.return_value = make_task(id=1, title=task_title, status=TaskStatus.DONE)

    with pytest.raises(InvalidTaskStatusTransition):
        await service.update_task_status(1, TaskStatus.NEW)

    mock_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_get_many_filter():
    repo = FakeTaskRepository()
    task_title = "Unit test get many"
    await repo.create(title=task_title)
    await repo.create(title=task_title)
    await repo.create(title=task_title, status=TaskStatus.PROCESSING)
    service = TaskService(repo)

    tasks = await service.get_many(status=TaskStatus.NEW)

    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_get_many_pagination():
    repo = FakeTaskRepository()
    for i in range(5):
        await repo.create(title=f"Unit test get many {i}")
    service = TaskService(repo)

    tasks = await service.get_many(limit=2, offset=2)

    assert len(tasks) == 2
    assert tasks[0].id == 3
    assert tasks[1].id == 4


@pytest.mark.asyncio
async def test_get_many_empty():
    repo = FakeTaskRepository()
    service = TaskService(repo)

    tasks = await service.get_many()

    assert tasks == []

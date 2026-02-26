import pytest

from app.domain.enums import TaskStatus


@pytest.mark.asyncio
async def test_create_task_success(async_client):
    task_title = "Test create task"
    response = await async_client.post(
        "/api/tasks/",
        json={"title": task_title},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == task_title
    assert data["status"] == TaskStatus.NEW.value
    assert data["result"] is None


@pytest.mark.asyncio
async def test_create_task_empty_title(async_client):
    response = await async_client.post(
        "/api/tasks/",
        json={"title": ""},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_task_success(async_client, create_task):
    task_title = "Test get task"
    task = await create_task(task_title)

    response = await async_client.get(f"/api/tasks/{task.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task.id
    assert data["title"] == task_title


@pytest.mark.asyncio
async def test_get_task_not_found(async_client):
    response = await async_client.get("/api/tasks/9999/")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_tasks_list(async_client, create_task):
    task_title = "Test get tasks list"
    await create_task(task_title)
    await create_task(task_title)

    response = await async_client.get("/api/tasks/")

    assert response.status_code == 200

    data = response.json()
    assert data["count"] >= 2
    assert len(data["items"]) >= 2
    assert any([task["title"] == task_title for task in data["items"]])


@pytest.mark.asyncio
async def test_get_tasks_filter_by_status(async_client, create_task):
    task_title = "Test get tasks filter by status"
    await create_task(task_title, status=TaskStatus.PROCESSING)

    response = await async_client.get("/api/tasks/?task_status=processing")

    assert response.status_code == 200

    data = response.json()
    assert data["count"] >= 1
    assert all(task["status"] == "processing" for task in data["items"])
    assert any([task["title"] == task_title for task in data["items"]])


@pytest.mark.asyncio
async def test_get_tasks_pagination(async_client, create_task):
    response = await async_client.get("/api/tasks/")
    exist_tasks = response.json()["items"]
    for i in range(5):
        await create_task(f"Test get tasks pagination {i}", status=TaskStatus.PROCESSING)
    limit = 2
    offset = len(exist_tasks)
    response = await async_client.get(f"/api/tasks/?limit={limit}&offset={offset}")

    assert response.status_code == 200
    data = response.json()

    assert len(data["items"]) == 2
    assert all(task["status"] == "processing" for task in data["items"])

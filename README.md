# Task Handler

## Описание проекта

Мини-сервис предназначен для управления задачами с асинхронной обработкой. Пользователи могут создавать задачи, получать их список и детали, а фоновые воркеры обрабатывают задачи автоматически, обновляя статус и результат.

Документация API доступна по адресу [http://localhost/docs](http://localhost/docs)

---

## Реализованные эндпоинты

| Метод | Путь                        | Описание                                                                |
|-------|-----------------------------|-------------------------------------------------------------------------|
| POST  | `/tasks/`                   | Создание задачи                                                         |
| GET   | `/tasks/{task_id}/`         | Получение одной задачи                                                  |
| GET   | `/tasks/?status={status}`   | Получение списка задач с возможностью фильтрации по статусу и пагинации |

---

## Фоновая задача

* При создании задачи сервис создаёт фоновую задачу с помощью Redis
* Celery выполняет обработку задачи:
  * Обновляет статус задачи `update_task_status(task_id, TaskStatus.PROCESSING)`
  * Тяжелые вычислительные процессы `time.sleep(3)`
  * По количеству символов в title принимает значение для `status` и `result` (Если длина title нечётная → failed, если чётная → done)
  * Обновление статуса `update_task_status(task_id, new_status)`
  * Обновление result `update_result(task_id, result)`


---

## Используемые технологии

* Python 3.13
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* PostgreSQL
* Redis
* Celery
* Docker
* Docker Compose
* pytest

---

## Как запустить проект

1. Клонировать репозиторий:
```
git clone https://github.com/berg96/task_handler_testtask_softway
```
2. Перейти в папку проекта:
```
cd task_handler_testtask_softway
```
3. Создать файл .env на основе примера .env_example и заполнить переменные окружения:

4. Запустить все сервисы через Docker Compose:
```
docker compose up -d
```

Документация API при запущенных контейнерах доступна по следующему адресу:
[http://localhost/docs](http://localhost/docs)

---

### Автор проекта

**Артём Куликов**  

Telegram: [@Berg1005](https://t.me/berg1005)

GitHub: [https://github.com/berg96](https://github.com/berg96)

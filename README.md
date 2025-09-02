### Task Manager — это REST API для управления задачами, написанный на FastAPI и использующий PostgreSQL в качестве основной базы данных. Приложение поддерживает CRUD-операции, фильтрацию, управление статусами и развертывается с помощью Docker. Доступны тесты локально на SQLite и отдельно в контейнере на PostgreSQL.

<details>
<summary>Автор</summary>

* [Github](https://github.com/avdeevdmitrykrsk)
* [Telegram](https://t.me/h0mie_s)

</details>

<details>
<summary>Стек</summary>

- python 3.11
- fastapi
- postgresql
- sqlalchemy
- pydantic
- pytest

</details>

## Приложение имеет 3 режима работы
### 1 - `debug_mode=local`
### Данный режим предназначен для локального тестирования приложения на sqlite.
### 2 - `debug_mode=docker`
### Данный режим предназначен для тестирования БД в docker-контейнере, тесты так же будут использовать контейнер для проверки.
### 3- `debug_mode=False`
### Продакшен режим, всё приложение будет развернуто в docker-контейнерах под управлением docker-compose.

## Развертывание проекта
* Склонировать репозиторий
```bash
git clone https://github.com/avdeevdmitrykrsk/task_manager.git
```

* Установить зависимости в виртуальное окружение
```bash
pip install -r requirements
```

* Настроить файл `.env` по примеру из `.env.example`

## Запуск проекта
### Запуск для разработки локально на `sqlite`
* Устанавливаем `debug_mode=local`
* Создаем миграции `alembic`
* Применяем миграции
* Запускаем uvicorn
```bash
uvicorn app.main:app --reload
```
* Разрабатываем.

> [!WARNING]
> Обязательно указываем разные `--project-name`, иначе будут конфликты тестовой и прод БД.
### Запуск для разработки с БД в docker-контейнере.
* Устанавливаем `debug_mode=docker`
* Создаем миграции `alembic`
* Применяем миграции
* Запускаем контейнер через тестовый `docker-compose`, контейнер запустится на порту `5433`.
```bash
docker-compose -f docker-compose.test.yml -p task_manager_test up --build
```

### Запуск в продакшен
* Устанавливаем `debug_mode=False`
* Запускаем контейнеры, миграции создаются и применяются автоматически в контейнере.

docker-compose -p task_manager_prod up --build
```
## Примеры запросов

### Создание задачи: `/api/tasks/`. По дефолту задача создается со статусом `Создано`.

`Запрос`
```json
{
    "name": "Новая задача",
    "description": "Описание задачи"
}
```
`Ответ(201 Created)`
```json
{
  "id": "735adbe8-063b-44e6-9e45-bdc0b010fb01",
  "name": "Новая задача",
  "description": "Описание задачи",
  "status": "Создано",
  "created_at": "2025-08-30T10:00:00",
  "updated_at": "2025-08-30T10:00:00"
}
```
### Получение списка задач: Доступна `query-фильтрация` по `status`, `name`, `description`. 
`Запрос` 
```http
/api/tasks?status=В работе
```
`Ответ(200 OK)`
```json
[
  {
    "id": "735adbe8-063b-44e6-9e45-bdc0b010fb01",
    "name": "Новая задача",
    "description": "Описание задачи",
    "status": "Создано",
    "created_at": "2025-08-30T09:00:00",
    "updated_at": "2025-08-30T10:00:00"
  }
]
```
### Обновление задачи: Состояния обновления статуса:
#### `Создано` -> `В работе`
#### `В работе` -> `Завершено`
#### `Завершено` -> `В работе`
`Запрос`
`/api/tasks/735adbe8-063b-44e6-9e45-bdc0b010fb01`

```json
{
  "status": "В работе"
}
```
`Ответ(200 OK)`
```json
{
    "id": "735adbe8-063b-44e6-9e45-bdc0b010fb01",
    "name": "Новая задача",
    "description": "Описание задачи",
    "status": "В работе",
    "created_at": "2025-08-30T09:00:00",
    "updated_at": "2025-08-30T10:00:00"
  }
```
## Websocket
### Connect `ws://<host>/api/tasks/ws`
### `event types:`
```python
"task_created", "task_updated", "task_deleted"
```
```json
{
    "event": "task_updated",
    "data": {
        "id": "735adbe8-063b-44e6-9e45-bdc0b010fb01",
        "name": "Новая задача",
        "description": "Описание задачи",
        "status": "В работе",
        "created_at": "2025-08-30T09:00:00",
        "updated_at": "2025-08-30T10:00:00"
    },
}
```

## Тесты
### Все тесты запускаются из корневой директории командой `pytest`, предварительно не забыв сделать миграции и выставить необходимый режим, тесты работают с режимами `debug_mode=local` и `debug_mode=docker`

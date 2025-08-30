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
* Запускаем uvicorn
```bash
uvicorn app.main:app --reload
```
* Разрабатываем.

### Запуск для разработки с БД в docker-контейнере.
* Устанавливаем `debug_mode=docker`
* Создаем миграции `alembic`
* Применяем миграции
* Запускаем контейнер через тестовый `docker-compose`, контейнер запустится на порту `5433`
```bash
docker-compose -f docker-compose.test.yml -p task_manager_test up --build
```

### Запуск в продакшен
* Устанавливаем `debug_mode=False`
* Запускаем контейнеры, миграции создаются и применяются автоматически в контейнере, обязательно указываем `--project-name` иначе будут конфликты тестовой и прод БД.
```bash
docker-compose -p task_manager_prod up --build
```
## Тесты
### Все тесты запускаются из корневой директории командой `pytest`, предварительно не забыв сделать миграции и выставить необходимый режим, тесты работают с режимами `debug_mode=local` и `debug_mode=docker`

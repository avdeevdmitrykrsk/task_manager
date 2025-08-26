# Standart lib imports
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Thirdparty imports
from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

load_dotenv()

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    # project
    debug_mode: bool = Field(default=False, description='Режим отладки')
    secret_key: Optional[str] = Field(
        default=None, description='Секретный ключ приложения'
    )

    # postgres
    postgres_db: Optional[str] = Field(default=None, description='Название БД')
    postgres_user: Optional[str] = Field(
        default=None, description='Пользователь БД'
    )
    postgres_password: Optional[str] = Field(
        default=None, description='Пароль БД'
    )
    db_host: str = Field(default='localhost', description='Хост БД')
    db_port: str = Field(default='5432', description='Порт БД')

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='',
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        """Строка подключения к postgres/sqlite DB."""

        if self.debug_mode:
            return 'sqlite+aiosqlite:///test.db'

        if not all(
            [
                self.postgres_user,
                self.postgres_password,
                self.postgres_db,
                self.db_host,
                self.db_port,
            ]
        ):
            raise ValueError("Отсутствуют обязательные настройки PostgreSQL")

        return (
            f'postgresql+asyncpg://'
            f'{self.postgres_user}:{self.postgres_password}'
            f'@{self.db_host}:{self.db_port}/{self.postgres_db}'
        )


def setup_logging():
    """Настройка логгера."""

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=LOG_DIR / 'app.log', encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


settings = Settings()

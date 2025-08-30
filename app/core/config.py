# Standart lib imports
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

# Thirdparty imports
from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

load_dotenv()

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    # project
    debug_mode: Union[bool, str] = Field(
        default=True, description='Режим отладки'
    )
    secret_key: Optional[str] = Field(
        default=None, description='Секретный ключ приложения'
    )

    # postgres
    pg_db: Optional[str] = Field(default='test_db', description='Название БД')
    pg_user: Optional[str] = Field(
        default='user', description='Пользователь БД'
    )
    pg_password: Optional[str] = Field(
        default='password', description='Пароль БД'
    )

    # pytest
    postgres_test_user: Optional[str] = Field(
        default=None, description='Тест-пользователь в БД'
    )
    postgres_test_password: Optional[str] = Field(
        default=None, description='Тест-пароль в БД'
    )
    postgres_test_db: Optional[str] = Field(
        default=None, description='Название тестовой БД'
    )

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='',
        case_sensitive=False,
        extra='ignore',
    )

    @property
    def db_host(self) -> str:
        return 'db' if self.debug_mode == 'False' else 'localhost'

    @property
    def db_port(self) -> int:
        return '5433' if self.debug_mode == 'docker' else '5432'

    @property
    def postgres_user(self) -> str:
        return (
            self.pg_user
            if self.debug_mode == 'False'
            else self.postgres_test_user
        )

    @property
    def postgres_password(self) -> str:
        return (
            self.pg_password
            if self.debug_mode == 'False'
            else self.postgres_test_password
        )

    @property
    def postgres_db(self) -> str:
        return (
            self.pg_db if self.debug_mode == 'False' else self.postgres_test_db
        )

    @property
    def database_url(self) -> str:
        if self.debug_mode == 'local':
            return 'sqlite+aiosqlite:///test.db'
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

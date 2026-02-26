from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = Field("Task Handler", description="Название приложения")
    APP_DESCRIPTION: str = Field(
        "Сервис управления задачами с асинхронной обработкой", description="Описание приложения"
    )

    DB_TYPE: str = Field("postgresql", description="Тип БД")
    DB_CONNECTOR: str = Field("asyncpg", description="Коннектор к БД")
    POSTGRES_DB: str = Field(..., description="Название БД")
    POSTGRES_USER: str = Field(..., description="Имя пользователя БД")
    POSTGRES_PASSWORD: str = Field(..., description="Пароль БД")
    POSTGRES_CONTAINER: str = Field("localhost", description="Имя контейнера с БД")
    POSTGRES_PORT: int = Field(5432, description="Порт БД")

    DB_SCHEMA: str = Field("tasks", description="Имя схемы БД")

    REDIS_URL: str = Field(..., description="URL подключения к Redis")

    LIMIT_DEFAULT: int = Field(50, description="Количество элементов при пагинации по умолчанию")
    OFFSET_DEFAULT: int = Field(0, description="Смещение элементов при пагинации по умолчанию")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_db_url(self):
        encoded_password = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"{self.DB_TYPE}+{self.DB_CONNECTOR}://"
            f"{self.POSTGRES_USER}:{encoded_password}@"
            f"{self.POSTGRES_CONTAINER}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()

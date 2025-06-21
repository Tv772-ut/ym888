from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    ADMIN_USER_IDS: List[int] = []
    DB_URL: str = "sqlite+aiosqlite:///data.db"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

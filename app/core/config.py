from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# print(BASE_DIR/ '.env')


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


class DbSettings(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="DB_")
    url: str
    test_url: str
    echo: bool


class RedisSettings(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="REDIS_")
    user: str
    user_password: int


class SuperUserSettings(BaseConfig):
    model_config = SettingsConfigDict(env_prefix="super_user_")
    USERNAME: str
    PASSWORD: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")
    db: DbSettings = Field(default_factory=DbSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    super_user: SuperUserSettings = Field(default_factory=SuperUserSettings)
    secret_key: str
    debug: bool
    mode: Literal["PROD", "DEV"] = "DEV"
    salt: str
    version: str


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
# print(settings)

mini_db = []

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

DOTENV = os.path.join("/Users/the_alive/ALL_PYTHON_PROJECTS/async_ChatGPT/.env")


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    TG_KEY: str

    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=DOTENV)


settings = Settings()

from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/krishiquery"
    API_KEY: str = "dev_key"

    class Config:
        env_file = ".env"

settings = Settings()
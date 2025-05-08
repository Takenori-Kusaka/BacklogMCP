from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    READ_ONLY_MODE: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
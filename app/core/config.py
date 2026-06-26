import os

from pydantic_settings import BaseSettings


ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
)


if ENVIRONMENT == "production":
    env_file = ".env.production"

else:
    env_file = ".env.development"


class Settings(BaseSettings):

    JWT_SECRET: str

    GROQ_API_KEY: str

    DATABASE_URL: str

    ENVIRONMENT: str

    class Config:
        env_file = env_file


settings = Settings()
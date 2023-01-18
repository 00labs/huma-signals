import os
from enum import Enum
from pathlib import Path

import dotenv
import pydantic


class Env(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    TESTNET = "testnet"
    PRODUCTION = "production"


ENV = os.getenv("ENV")
if ENV in (Env.PRODUCTION, Env.STAGING, Env.TESTNET):
    env_path = Path(__file__).parent / "dotenv" / ".env"
elif ENV == Env.TEST:
    env_path = Path(__file__).parent / "dotenv" / "test.env"
elif ENV == Env.DEVELOPMENT:
    env_path = Path(__file__).parent / "dotenv" / "development.env"
elif ENV is None:
    raise ValueError("No ENV is defined")
else:
    raise ValueError(f"Unknown ENV: {ENV}")

# Load environment variables from .env file
# Note they won't override existing environment variables
dotenv.load_dotenv(dotenv_path=env_path)


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    env: str
    sentry_dsn: str


settings = Settings()

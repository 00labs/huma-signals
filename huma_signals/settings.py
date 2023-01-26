# pylint: disable=too-few-public-methods
import enum
import os
import pathlib

import dotenv
import pydantic


class Env(str, enum.Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    TESTNET = "testnet"
    PRODUCTION = "production"


ENV = os.getenv("ENV")
if ENV in (Env.PRODUCTION, Env.STAGING, Env.TESTNET):
    # For ECS services, no .env is loaded.
    env_path = None
elif ENV == Env.TEST:
    env_path = pathlib.Path(__file__).parent / "dotenv" / "test.env"
elif ENV == Env.DEVELOPMENT:
    env_path = pathlib.Path(__file__).parent / "dotenv" / "development.env"
elif ENV is None:
    raise ValueError("No ENV is defined")
else:
    raise ValueError(f"Unknown ENV: {ENV}")

# Load environment variables from .env file
# Note they won't override existing environment variables
if env_path:
    dotenv.load_dotenv(dotenv_path=env_path)


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    env: str
    sentry_dsn: str

    # For the ethereum_wallet adapter
    etherscan_api_key: str


settings = Settings()

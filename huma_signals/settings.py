import enum
import os
import pathlib

import dotenv
import pydantic
from huma_utils import chain_utils


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
elif not ENV:
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
    chain: chain_utils.Chain
    web3_provider_url: str

    instrumentation_enabled: bool
    datadog_api_key: str

    # adapter: allowlist
    allow_list_endpoint: str = "https://dev.allowlist.huma.finance/"

    # adapter: ethereum_wallet
    etherscan_base_url: str = "https://api.etherscan.io"
    etherscan_api_key: str

    # adapter: polygon_wallet
    polygonscan_base_url: str = "https://api.polygonscan.com"
    polygonscan_api_key: str

    # adapter: request_network
    request_network_subgraph_endpoint_url: str
    request_network_invoice_api_url: str


settings = Settings()

import pydantic
from huma_utils import chain_utils


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    chain: chain_utils.Chain
    superfluid_subgraph_endpoint_url: str


settings = Settings()

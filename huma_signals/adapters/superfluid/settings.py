import pydantic

from huma_signals.commons import chains


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    chain: chains.Chain
    superfluid_subgraph_endpoint_url: str


settings = Settings()

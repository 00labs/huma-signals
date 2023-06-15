import pydantic
from huma_utils import chain_utils


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    chain: chain_utils.Chain
    request_network_subgraph_endpoint_url: str
    request_network_invoice_api_url: str


settings = Settings()

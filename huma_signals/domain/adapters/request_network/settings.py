import pydantic

from huma_signals.commons import chains


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    chain: chains.Chain
    request_network_subgraph_endpoint_url: str
    request_network_invoice_api_url: str


settings = Settings()

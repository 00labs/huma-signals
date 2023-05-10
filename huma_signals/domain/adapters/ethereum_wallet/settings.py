import pydantic


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    etherscan_base_url: str
    etherscan_api_key: str


settings = Settings()

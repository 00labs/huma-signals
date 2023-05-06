import pydantic


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    web3_provider_url: str


settings = Settings()

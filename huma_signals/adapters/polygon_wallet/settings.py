import pydantic


class Settings(pydantic.BaseSettings):
    class Config:
        case_sensitive = False

    polygonscan_base_url: str = "https://api.polygonscan.com"
    polygonscan_api_key: str


settings = Settings()

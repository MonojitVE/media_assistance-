from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    media_root: str = "./media"
    short_media_threshold_sec: int = 120
    groq_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    media_root: str = "./media"
    short_media_threshold_sec: int = 120
    groq_api_key: str = ""
    client_id: str = ""
    client_secret: str = ""
    google_redirect_uri: str = "http://localhost:5173" # Frontend port
    frontend_url: str = "http://localhost:3000" # Allowed CORS origin

    class Config:
        env_file = ".env"


settings = Settings()

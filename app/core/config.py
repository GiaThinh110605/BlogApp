from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Todo Application"
    debug: bool = True
    api_v1_str: str = "/api/v1"

    class Config:
        env_file = "/Users/mac/BlogApp/.env"
        case_sensitive = False

settings = Settings()
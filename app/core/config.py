from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Todo Application"
    debug: bool = True
    api_v1_str: str = "/api/v1"
    
    # Database configuration
    database_url: str = "sqlite:///./blog_app.db"
    
    class Config:
        env_file = "/Users/mac/BlogApp/.env"
        case_sensitive = False

settings = Settings()
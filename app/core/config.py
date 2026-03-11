from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI Todo Application"
    debug: bool = True
    api_v1_str: str = "/api/v1"
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    
    # Database configuration
    database_url: str = "sqlite:///./blog_app.db"
    
    class Config:
        env_file = "/Users/mac/BlogApp/.env"
        case_sensitive = False

settings = Settings()
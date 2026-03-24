from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    app_name: str = "Prompt Manager"
    database_url: str = "sqlite:///./prompts.db"
    upload_dir: str = "./uploads"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    
    class Config:
        env_file = ".env"


settings = Settings()

os.makedirs(settings.upload_dir, exist_ok=True)
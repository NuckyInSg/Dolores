from pydantic_settings import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Robert"
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:8080"]
    UPLOAD_DIR: str = "./docs"
    
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

    # API URLs
    ANTHROPIC_API_URL: str = "https://api.anthropic.com"
    OPENAI_API_URL: str = "https://api.openai.com/v1"

    # Supported models
    SUPPORTED_MODELS: Dict[str, Dict[str, str]] = {
        "claude-3-sonnet-20240229": {
            "provider": "anthropic",
            "name": "claude-3-sonnet-20240229",
            "temperature": 0,
            "api_key": "ANTHROPIC_API_KEY",
            "api_url": "ANTHROPIC_API_URL"
        },
        "claude-3-opus-20240229": {
            "provider": "anthropic",
            "name": "claude-3-opus-20240229",
            "temperature": 0,
            "api_key": "ANTHROPIC_API_KEY",
            "api_url": "ANTHROPIC_API_URL"
        },
        "gpt-4": {
            "provider": "openai",
            "name": "gpt-4",
            "temperature": 0,
            "api_key": "OPENAI_API_KEY",
            "api_url": "OPENAI_API_URL"
        },
        "gpt-3.5-turbo": {
            "provider": "openai",
            "name": "gpt-3.5-turbo",
            "temperature": 0,
            "api_key": "OPENAI_API_KEY",
            "api_url": "OPENAI_API_URL"
        }
    }

    class Config:
        env_file = ".env"

settings = Settings()
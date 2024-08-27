from pydantic_settings import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dolores"
    ALLOWED_ORIGINS: List[str] = ["http://localhost", "http://localhost:8080"]
    UPLOAD_DIR: str = "./docs"
    
    # API Keys
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str

    # API URLs
    ANTHROPIC_API_URL: str = "https://api.anthropic.com"
    OPENAI_API_URL: str = "https://api.openai.com/v1"

    # Supported models
    SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
        "claude-3-5-sonnet-20240620": {
            "provider": "anthropic",
            "name": "claude-3-5-sonnet-20240620",
            "api_key": "ANTHROPIC_API_KEY",
            "api_url": "ANTHROPIC_API_URL",
            "extra_info": {
                "encoder": "cl100k_base",
                "context_window": 200000,
                "max_output_token": 8192,
                "cost_input": 3.00,
                "cost_output": 15.00
            }
        },
        "claude-3-sonnet-20240229": {
            "provider": "anthropic",
            "name": "claude-3-sonnet-20240229",
            "api_key": "ANTHROPIC_API_KEY",
            "api_url": "ANTHROPIC_API_URL"
        },
        "claude-3-opus-20240229": {
            "provider": "anthropic",
            "name": "claude-3-opus-20240229",
            "api_key": "ANTHROPIC_API_KEY",
            "api_url": "ANTHROPIC_API_URL"
        },
        "gpt-4": {
            "provider": "openai",
            "name": "gpt-4",
            "api_key": "OPENAI_API_KEY",
            "api_url": "OPENAI_API_URL"
        },
        "gpt-3.5-turbo": {
            "provider": "openai",
            "name": "gpt-3.5-turbo",
            "api_key": "OPENAI_API_KEY",
            "api_url": "OPENAI_API_URL"
        }
    }

    class Config:
        env_file = ".env"

settings = Settings()
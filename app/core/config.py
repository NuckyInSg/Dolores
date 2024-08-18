from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Interview System"
    ALLOWED_ORIGINS: list = ["http://localhost", "http://localhost:8080"]
    UPLOAD_DIR: str = "./uploads"
    ANTHROPIC_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

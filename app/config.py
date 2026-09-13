import os
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()

@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


settings = Settings()

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MEMORY_FILE = BASE_DIR / "data" / "memory.json"


@dataclass
class Settings:
    telegram_bot_token: str
    openai_api_key: str
    openai_model: str
    morning_hour: int
    morning_minute: int
    memory_file: Path


def get_settings() -> Settings:
    load_dotenv()

    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    morning_hour = int(os.getenv("MORNING_HOUR", "9"))
    morning_minute = int(os.getenv("MORNING_MINUTE", "0"))

    if not telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    return Settings(
        telegram_bot_token=telegram_bot_token,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        morning_hour=morning_hour,
        morning_minute=morning_minute,
        memory_file=DEFAULT_MEMORY_FILE,
    )

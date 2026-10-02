import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file (with fallback to .env.example)
if (BASE_DIR / ".env").exists():
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
elif (BASE_DIR / ".env.example").exists():
    load_dotenv(dotenv_path=BASE_DIR / ".env.example", override=True)


# Active Groq production models
PRIMARY_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
]


class Settings:
    """Application configuration settings loaded from environment variables."""

    GROQ_API_KEY: str = ""
    SESSION_PIN: str = "123456"
    PORT: int = 8000
    PRIMARY_MODELS: list[str] = PRIMARY_MODELS
    MODEL_NAME: str = PRIMARY_MODELS[0]

    def __init__(self):
        self.reload()

    def reload(self):
        if (BASE_DIR / ".env").exists():
            load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
        elif (BASE_DIR / ".env.example").exists():
            load_dotenv(dotenv_path=BASE_DIR / ".env.example", override=True)

        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
        self.SESSION_PIN = os.getenv("SESSION_PIN", "123456").strip()
        self.PORT = int(os.getenv("PORT", "8000"))
        self.PRIMARY_MODELS = PRIMARY_MODELS
        self.MODEL_NAME = os.environ.get("GROQ_MODEL", PRIMARY_MODELS[0])

    def verify_session_pin(self, provided_pin: str) -> bool:
        """
        Validate whether the student's provided PIN matches the active lab session PIN.
        Uses constant-time comparison to prevent timing side-channel attacks.
        """
        if not provided_pin:
            return False
        return secrets.compare_digest(provided_pin.strip(), self.SESSION_PIN)


# Global settings singleton
settings = Settings()

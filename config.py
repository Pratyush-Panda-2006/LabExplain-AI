import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(dotenv_path=BASE_DIR / ".env")


class Settings:
    """Application configuration settings loaded from environment variables."""

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    SESSION_PIN: str = os.getenv("SESSION_PIN", "123456").strip()
    PORT: int = int(os.getenv("PORT", "8000"))
    MODEL_NAME: str = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

    @classmethod
    def verify_session_pin(cls, provided_pin: str) -> bool:
        """
        Validate whether the student's provided PIN matches the active lab session PIN.
        Uses constant-time comparison to prevent timing side-channel attacks.
        """
        if not provided_pin:
            return False
        return secrets.compare_digest(provided_pin.strip(), cls.SESSION_PIN)


# Global settings singleton
settings = Settings()

# =============================================================================
# Application settings loaded from environment variables.
# The app reads configuration here once at import time; `database.py` uses DATABASE_URL.
# =============================================================================

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

# Project root = folder that contains `app/` and `.env`
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load variables from `.env` into os.environ
load_dotenv(PROJECT_ROOT / ".env")

# PostgreSQL connection (from .env)
POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5433")
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "job_bank")

# App settings
APP_TITLE: str = os.getenv("APP_TITLE", "My Job Bank App")
APP_ENV: str = os.getenv("APP_ENV", "development")  # development | production
DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")

# Folder where uploaded resumes/docs are stored (served at /uploads/...)
UPLOAD_DIR: Path = PROJECT_ROOT / "uploads"
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))


def build_database_url() -> str:
    """
    Build a SQLAlchemy PostgreSQL URL from POSTGRES_* variables.

    Special characters in passwords are URL-encoded automatically.
    """
    safe_password = quote_plus(POSTGRES_PASSWORD)
    base = (
        f"postgresql://{POSTGRES_USER}:{safe_password}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    return base

DATABASE_URL: str = os.getenv("DATABASE_URL") or build_database_url()

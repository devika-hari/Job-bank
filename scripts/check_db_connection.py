# =============================================================================
# Verify PostgreSQL credentials from `.env` before starting the API.
# Usage (from project root, with venv active): python scripts/check_db_connection.py
# =============================================================================


import sys
from pathlib import Path

# Allow `python scripts/check_db_connection.py` from project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text
from app.config import DATABASE_URL, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER


def main() -> int:
    print(f"Connecting as user={POSTGRES_USER} host={POSTGRES_HOST} port={POSTGRES_PORT} db={POSTGRES_DB}")
    engine = create_engine(DATABASE_URL, echo=False)
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar_one()
        print("Connection OK.")
        print(version[:80] + "...")
        return 0
    except Exception as exc:
        print("Connection FAILED:", exc, file=sys.stderr)
        print("Check POSTGRES_* values in .env and that PostgreSQL is running.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

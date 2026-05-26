# =============================================================================
# Create POSTGRES_DB if it does not exist - by checking in pg_database
# Connects to the default `postgres` database using credentials from `.env`.
# Usage:  python scripts/create_database.py
# =============================================================================


import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

from dotenv import load_dotenv
import os

load_dotenv(ROOT / ".env")

user = os.getenv("POSTGRES_USER", "postgres")
password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5433")
db_name = os.getenv("POSTGRES_DB", "job_bank")

# You cannot create a database unless already connected to SOME database
# So connect to postgres DB(default admin DB), then create your own DB
admin_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
# creates:DB connection configuration, connection pool, communication layer
# AUTOCOMMIT: Execute immediately, Do not wrap in transaction (both CREATE/DROP DB)
engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

with engine.connect() as conn:
    exists = conn.execute(
        text("SELECT 1 FROM pg_database WHERE datname = :name"),
        {"name": db_name},
    ).scalar()
    if exists:
        print(f"Database '{db_name}' already exists.")
    else:
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        print(f"Created database '{db_name}'.")

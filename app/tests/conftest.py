# =============================================================================
# Test setup — uses SQLite in memory so pytest works without PostgreSQL.
# IMPORTANT: Set DATABASE_URL in .env before importing app modules so SQLAlchemy
# uses SQLite instead of your local PostgreSQL instance.
# =============================================================================


import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Reconfigure the shared engine for in-memory SQLite tests
import app.database as db_module

db_module.engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_module.engine)

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=db_module.engine)
    session = db_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=db_module.engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

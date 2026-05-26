from fastapi import FastAPI
from app.database import init_db, seed_default_user, SessionLocal

app = FastAPI()

@app.on_event("startup")
def startup():
    # 1. Create tables
    init_db()

    # 2. Seed default user
    db = SessionLocal()
    try:
        seed_default_user(db)
    finally:
        db.close()
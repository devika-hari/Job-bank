# =============================================================================
# ALL database interactions setup:
# - connection to PostgreSQL
# - session handling per request
# - table creation
# =============================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import DATABASE_URL

# Echo =false - clean logs
engine = create_engine(DATABASE_URL, echo=False)

# each API request should get its own session to avoid data leaks between requests, concurrency issues
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creates base class for ALL ORM models (tables are subclasses of Base)
Base = declarative_base()

#Provides a DB session to every API request.
def get_db():
    # Open session at start of request
    db = SessionLocal()
    try:
        # Pass session to route
        yield db
    finally:
        db.close()

# Create all tables if they do not exist yet
def init_db():
    # Import models so SQLAlchemy registers all tables on Base.metadata & create, if doesn't exist
    from app import models
    Base.metadata.create_all(bind=engine)

# Create one demo user so the app works without login
def seed_default_user(db):
    from app.models.user import User
    existing = db.query(User).filter(User.email == "demo@jobbank.local").first()
    if existing:
        return existing
    #demo user
    user = User(name="Demo User", email="demo@jobbank.local")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# =============================================================================
# User model — one person tracking many job applications
# RELATIONSHIP: User (1) -> (*) JobApplied
# =============================================================================


from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # back_populates links this side to JobApplied.user
    # jobs -> virtual list of related JobApplied objects, Not stored in User table
    jobs = relationship("JobApplied", back_populates="user", cascade="all, delete-orphan")

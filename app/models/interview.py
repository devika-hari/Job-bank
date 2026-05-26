# =============================================================================
# Interview round model — each job can have multiple interview rounds
# RELATIONSHIP: Interview (1) -> (*) InterviewQuestion
# =============================================================================

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs_applied.id", ondelete="CASCADE"), nullable=False, index=True)

    round_number = Column(Integer, nullable=False, default=1)
    interview_date = Column(Date, nullable=True)
    interviewer_names = Column(String(500), nullable=True)
    round_status = Column(String(80), nullable=False, default="Scheduled")
    comments = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("JobApplied", back_populates="interviews")
    questions = relationship(
        "InterviewQuestion",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

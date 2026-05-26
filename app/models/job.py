# =============================================================================
# Job application model — core entity for the job bank
# RELATIONSHIP: JobApplied (1) -> (*) Interview
# =============================================================================


from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.database import Base


class JobApplied(Base):
    __tablename__ = "jobs_applied"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    role = Column(String(200), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    location = Column(String(200), nullable=True)
    job_description = Column(Text, nullable=True)

    employment_type = Column(String(80), nullable=True)  # e.g. Full-time, Contract
    workplace_type = Column(String(80), nullable=True)  # e.g. Remote, Hybrid, Onsite

    current_stage = Column(String(120), nullable=True)  # e.g. Phone screen, Onsite
    application_status = Column(String(80), nullable=False, default="Applied", index=True)

    rejection_reason = Column(Text, nullable=True)

    recruiter_name = Column(String(200), nullable=True, index=True)
    recruiter_email = Column(String(255), nullable=True)

    comments = Column(Text, nullable=True)
    # "Additional attachments" in the UI
    attachment_metadata = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="jobs")
    interviews = relationship(
        "Interview",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="Interview.round_number",
    )

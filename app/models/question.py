# =============================================================================
# Interview question model — questions per interview round
# RELATIONSHIP: many questions <-> many tags (see tag.py question_tags table)
# =============================================================================

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.tag import question_tags


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_text = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    interview = relationship("Interview", back_populates="questions")
    tags = relationship("Tag", secondary=question_tags, back_populates="questions")

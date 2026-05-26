# =============================================================================
# Tags, question_tags - mapping tags to questions
# RELATIONSHIP: InterviewQuestion (*) <-> (*) Tag via question_tags
# =============================================================================


from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

# Association table — only stores foreign keys (no extra business columns)
question_tags = Table(
    "question_tags",
    Base.metadata,
    Column("question_id", ForeignKey("interview_questions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    # Unique tag names like "Python", "SQL", "dbt"
    name = Column(String(100), unique=True, nullable=False, index=True)

    questions = relationship(
        "InterviewQuestion",
        secondary=question_tags,
        back_populates="tags",
    )

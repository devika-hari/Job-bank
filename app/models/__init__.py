# =============================================================================
# SQLAlchemy ORM models (database tables as Python classes)
# Import every model here so `from app import models` registers all tables.
# =============================================================================


from app.models.user import User
from app.models.job import JobApplied
from app.models.interview import Interview
from app.models.question import InterviewQuestion
from app.models.tag import Tag, question_tags

__all__ = [
    "User",
    "JobApplied",
    "Interview",
    "InterviewQuestion",
    "Tag",
    "question_tags",
]

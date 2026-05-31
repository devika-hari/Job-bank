from typing import List, Optional

from pydantic import BaseModel

from app.schemas.job import JobResponse
from app.schemas.question import QuestionResponse


class RecruiterSearchResult(BaseModel):
    company_name: str
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    job_id: int
    role: str


class RecruiterSearchResponse(BaseModel):
    total: int
    items: List[RecruiterSearchResult]


class JobSearchResponse(BaseModel):
    total: int
    items: List[JobResponse]


class QuestionSearchResponse(BaseModel):
    total: int
    items: List[QuestionResponse]


class TagStatsResponse(BaseModel):
    """pandas-powered summary for learning: count questions per tag."""
    tag: str
    question_count: int

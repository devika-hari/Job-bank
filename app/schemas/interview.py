from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class InterviewBase(BaseModel):
    round_number: int = Field(1, ge=1)
    interview_date: Optional[date] = None
    interviewer_names: Optional[str] = None
    round_status: str = "Scheduled"
    comments: Optional[str] = None

#child - metadata from db for future
class InterviewCreate(InterviewBase):
    #job_id comes from the URL path
    pass


class InterviewUpdate(BaseModel):
    round_number: Optional[int] = Field(None, ge=1)
    interview_date: Optional[date] = None
    interviewer_names: Optional[str] = None
    round_status: Optional[str] = None
    comments: Optional[str] = None


class InterviewResponse(InterviewBase):
    id: int
    job_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InterviewListResponse(BaseModel):
    total: int
    items: List[InterviewResponse]

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1)
    notes: Optional[str] = None
    # Tag names as strings; service will create tags if missing
    tags: List[str] = Field(default_factory=list)


class QuestionCreate(QuestionBase):
    # interview_id comes from the URL path
    pass


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class QuestionResponse(QuestionBase):
    id: int
    interview_id: int
    created_at: Optional[datetime] = None
    tag_details: List[TagResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class QuestionListResponse(BaseModel):
    total: int
    items: List[QuestionResponse]

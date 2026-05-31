# =============================================================================
# Pydantic models for job applications
# - Validates incoming JSON before it touches the database
# =============================================================================

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# common - parent
class JobBase(BaseModel):
    # ... -> Mandatory Field
    role: str = Field(..., min_length=1, max_length=200)
    company_name: str = Field(..., min_length=1, max_length=200)
    # Optional -> Optional field
    location: Optional[str] = None
    job_description: Optional[str] = None
    employment_type: Optional[str] = None
    workplace_type: Optional[str] = None
    current_stage: Optional[str] = None
    application_status: str = "Applied"
    rejection_reason: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[EmailStr] = None
    comments: Optional[str] = None
    attachment_metadata: Optional[str] = Field(
        default=None,
        description="Additional attachments — JSON list of uploaded file metadata",
    # description appears in Swagger docs
    )

# JobCreate - JobBase's child + user_id
class JobCreate(JobBase):
    # Body for POST /api/jobs — user_id optional (defaults to demo user)
    user_id: Optional[int] = None


class JobUpdate(BaseModel):
    #PATCH-update: every field optional
    role: Optional[str] = Field(None, min_length=1, max_length=200)
    company_name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = None
    job_description: Optional[str] = None
    employment_type: Optional[str] = None
    workplace_type: Optional[str] = None
    current_stage: Optional[str] = None
    application_status: Optional[str] = None
    rejection_reason: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[EmailStr] = None
    comments: Optional[str] = None
    attachment_metadata: Optional[str] = Field(
        default=None,
        description="Additional attachments — JSON list of uploaded file metadata",
    )

# add to JobBase - metadata fields from DB
class JobResponse(JobBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# GET /api/jobs, lists count of jobs and list of JobResponse objects
class JobListResponse(BaseModel):
    total: int
    items: List[JobResponse]

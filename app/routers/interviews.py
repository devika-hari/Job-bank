from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import not_found
from app.schemas.interview import (
    InterviewCreate,
    InterviewListResponse,
    InterviewResponse,
    InterviewUpdate,
)
#importing job service also
from app.services import interview_service, job_service

router = APIRouter(prefix="/api", tags=["Interviews"])

# GET /jobs/10/interviews
@router.get(
    "/jobs/{job_id}/interviews",
    response_model=InterviewListResponse,
    summary="List interviews for a job",
)

# first job check, then if job exists interview
def list_job_interviews(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        raise not_found("Job")
    items = interview_service.list_interviews_for_job(db, job_id)
    return InterviewListResponse(total=len(items), items=items)


@router.post(
    "/jobs/{job_id}/interviews",
    response_model=InterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add interview round to a job",
)
def create_interview(job_id: int, payload: InterviewCreate, db: Session = Depends(get_db)):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        raise not_found("Job")
    return interview_service.create_interview(db, job, payload)


@router.get("/interviews/{interview_id}", response_model=InterviewResponse, summary="Get interview")
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not interview:
        raise not_found("Interview")
    return interview


@router.put("/interviews/{interview_id}", response_model=InterviewResponse, summary="Update interview")
def update_interview(interview_id: int, payload: InterviewUpdate, db: Session = Depends(get_db)):
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not interview:
        raise not_found("Interview")
    return interview_service.update_interview(db, interview, payload)


@router.delete("/interviews/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not interview:
        raise not_found("Interview")
    interview_service.delete_interview(db, interview)

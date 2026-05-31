# =============================================================================
# Job application CRUD API routes alone (SQL in services)
# HTTP methods map to actions:
# - GET -> Read, POST -> Create, PATCH  -> Update, DELETE -> remove
# =============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import not_found
from app.schemas.job import JobCreate, JobListResponse, JobResponse, JobUpdate
from app.services import job_service


router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

# Calls list_jobs, response should match JobListResponse
@router.get("", response_model=JobListResponse, summary="List all job applications")
def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = job_service.list_jobs(db, skip=skip, limit=limit)
    return JobListResponse(total=len(items), items=items)

# Job by id
@router.get("/{job_id}", response_model=JobResponse, summary="Get one job by id")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        raise not_found("Job")
    return job

# CREATE JOB - JobCreate
@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED, summary="Create job")
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, payload)


@router.patch("/{job_id}", response_model=JobResponse, summary="Update job application")
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        raise not_found("Job")
    return job_service.update_job(db, job, payload)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete job")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        raise not_found("Job")
    job_service.delete_job(db, job)

# =============================================================================
# Job application business logic
# SQL query generation & execution
# =============================================================================

from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import seed_default_user
from app.models.job import JobApplied
from app.schemas.job import JobCreate, JobUpdate

# GET,PUT, DELETE /api/jobs/1
# SELECT * FROM jobs_applied WHERE JobApplied.id == job_id LIMIT 1
def get_job_or_none(db: Session, job_id: int) -> Optional[JobApplied]:
    return db.query(JobApplied).filter(JobApplied.id == job_id).first()

# GET /api/jobs
# SELECT * FROM jobs_applied ORDER BY created_at DESC LIMIT 100
def list_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[JobApplied]:
    return db.query(JobApplied).order_by(JobApplied.created_at.desc()).offset(skip).limit(limit).all()


def create_job(db: Session, payload: JobCreate) -> JobApplied:
    user_id = payload.user_id
    if user_id is None: #demo user
        user = seed_default_user(db)
        user_id = user.id

    # Building ORM object
    job = JobApplied(
        user_id=user_id,
        role=payload.role,
        company_name=payload.company_name,
        location=payload.location,
        job_description=payload.job_description,
        employment_type=payload.employment_type,
        workplace_type=payload.workplace_type,
        current_stage=payload.current_stage,
        application_status=payload.application_status,
        rejection_reason=payload.rejection_reason,
        recruiter_name=payload.recruiter_name,
        recruiter_email=str(payload.recruiter_email) if payload.recruiter_email else None,
        comments=payload.comments,
        attachment_metadata=payload.attachment_metadata,
    )
    # place job in SQLAlchemy session
    db.add(job)
    # SQLAlchemy executes SQL
    db.commit()
    # reloads obj from db to have id, created_at, updated_at (db generated values)
    db.refresh(job)
    return job # in router, pydantic converts to JSON


def update_job(db: Session, job: JobApplied, payload: JobUpdate) -> JobApplied:
    data = payload.model_dump(exclude_unset=True) #Only fields user actually sent
    if "recruiter_email" in data and data["recruiter_email"] is not None:
        data["recruiter_email"] = str(data["recruiter_email"])

    for field, value in data.items():
        setattr(job, field, value) # eg job.current_stage = "Technical Round"

    db.commit()
    db.refresh(job)
    return job

# DELETE FROM jobs_applied WHERE id=...
def delete_job(db: Session, job: JobApplied) -> None:
    # Masks rows for deletion
    db.delete(job)
    db.commit()

# BMW - WHERE company_name ILIKE '%BMW%'
def search_jobs_by_company(db: Session, company: str) -> List[JobApplied]:
    pattern = f"%{company.strip()}%"
    return (
        db.query(JobApplied)
        .filter(JobApplied.company_name.ilike(pattern))
        .order_by(JobApplied.company_name)
        .all()
    )

# WHERE role ILIKE '%Data Engineer%'
def search_jobs_by_role(db: Session, role: str) -> List[JobApplied]:
    pattern = f"%{role.strip()}%"
    return (
        db.query(JobApplied)
        .filter(JobApplied.role.ilike(pattern))
        .order_by(JobApplied.role)
        .all()
    )

# All Optional
def search_jobs(
    db: Session,
    company: Optional[str] = None,
    role: Optional[str] = None,
) -> List[JobApplied]:

    query = db.query(JobApplied)

    if company and company.strip():
        query = query.filter(JobApplied.company_name.ilike(f"%{company.strip()}%"))
    if role and role.strip():
        query = query.filter(JobApplied.role.ilike(f"%{role.strip()}%"))

    return query.order_by(JobApplied.created_at.desc()).all()

# Find recruiters by company -already talked with
def search_recruiters_by_company(db: Session, company: str) -> List[JobApplied]:
    pattern = f"%{company.strip()}%"
    return (
        db.query(JobApplied)
        .filter(JobApplied.company_name.ilike(pattern))
        .filter(JobApplied.recruiter_name.isnot(None))
        .all()
    )

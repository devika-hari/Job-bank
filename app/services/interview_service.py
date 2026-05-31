# =============================================================================
# Interview - Job Application business logic
# SQL query generation & execution
# =============================================================================
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.interview import Interview
from app.models.job import JobApplied
from app.schemas.interview import InterviewCreate, InterviewUpdate

# SELECT * FROM interviews WHERE id = interview_id LIMIT 1
def get_interview_or_none(db: Session, interview_id: int) -> Optional[Interview]:
    return db.query(Interview).filter(Interview.id == interview_id).first()

# SELECT * FROM interviews WHERE job_id = 10 ORDER BY round_number
def list_interviews_for_job(db: Session, job_id: int) -> List[Interview]:
    return (
        db.query(Interview)
        .filter(Interview.job_id == job_id)
        .order_by(Interview.round_number)
        .all()
    )


def create_interview(db: Session, job: JobApplied, payload: InterviewCreate) -> Interview:
    interview = Interview(
        job_id=job.id,
        round_number=payload.round_number,
        interview_date=payload.interview_date,
        interviewer_names=payload.interviewer_names,
        round_status=payload.round_status,
        comments=payload.comments,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


def update_interview(db: Session, interview: Interview, payload: InterviewUpdate) -> Interview:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)
    db.commit()
    db.refresh(interview)
    return interview


def delete_interview(db: Session, interview: Interview) -> None:
    db.delete(interview)
    db.commit()

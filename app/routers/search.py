# =============================================================================
# Search API routes — read-only endpoints for finding jobs and questions
# =============================================================================

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import bad_request
from app.schemas.job import JobResponse
from app.schemas.search import (
    JobSearchResponse,
    QuestionSearchResponse,
    RecruiterSearchResponse,
    RecruiterSearchResult,
    TagStatsResponse,
)
from app.services import job_service, question_service, search_service
from app.utils import question_to_response

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/jobs/by-company", response_model=JobSearchResponse, summary="Search jobs by company name")
def search_by_company(company: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    items = job_service.search_jobs_by_company(db, company)
    return JobSearchResponse(total=len(items), items=items)


@router.get("/jobs/by-role", response_model=JobSearchResponse, summary="Search jobs by role title")
def search_by_role(role: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    items = job_service.search_jobs_by_role(db, role)
    return JobSearchResponse(total=len(items), items=items)


@router.get("/jobs", response_model=JobSearchResponse, summary="Search jobs by company and/or role")
def search_jobs_combined(
    company: Optional[str] = Query(None, description="Partial company name"),
    role: Optional[str] = Query(None, description="Partial role title"),
    db: Session = Depends(get_db),
):
    if not (company and company.strip()) and not (role and role.strip()):
        raise bad_request("Provide at least one of: company, role")
    items = job_service.search_jobs(db, company=company, role=role)
    return JobSearchResponse(total=len(items), items=items)


@router.get(
    "/recruiters/by-company",
    response_model=RecruiterSearchResponse,
    summary="Find recruiter contacts for a company",
)
def search_recruiters(company: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    jobs = job_service.search_recruiters_by_company(db, company)
    items = [
        RecruiterSearchResult(
            company_name=j.company_name,
            recruiter_name=j.recruiter_name,
            recruiter_email=j.recruiter_email,
            job_id=j.id,
            role=j.role,
        )
        for j in jobs
    ]
    return RecruiterSearchResponse(total=len(items), items=items)


@router.get(
    "/questions/by-tags",
    response_model=QuestionSearchResponse,
    summary="Search interview questions by one or more tags",
)
def search_questions_by_tags(
    tags: Optional[List[str]] = Query(None, description="Repeat ?tags=Python&tags=SQL"),
    tags_csv: Optional[str] = Query(None, description="Comma-separated tags: Python,SQL"),
    db: Session = Depends(get_db),
):
    tag_list: List[str] = []
    if tags:
        tag_list.extend(tags)
    if tags_csv:
        tag_list.extend([t.strip() for t in tags_csv.split(",") if t.strip()])

    if not tag_list:
        raise bad_request("Provide tags via ?tags=Python or ?tags_csv=Python,SQL")

    items = question_service.search_questions_by_tags(db, tag_list)
    return QuestionSearchResponse(
        total=len(items),
        items=[question_to_response(q) for q in items],
    )


@router.get("/tags/stats", response_model=List[TagStatsResponse], summary="Tag counts (pandas)")
def tag_stats(db: Session = Depends(get_db)):
    return search_service.tag_question_stats(db)

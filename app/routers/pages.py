# =============================================================================
# Simple HTML pages using Jinja2 templates + Bootstrap
# =============================================================================

from datetime import date
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.config import APP_TITLE
from app.database import get_db
from app.models.job import JobApplied
from app.models.interview import Interview
from app.models.question import InterviewQuestion
from app.schemas.interview import InterviewCreate
from app.schemas.job import JobCreate
from app.schemas.question import QuestionCreate
from app.services import interview_service, job_service, question_service
from app.services.upload_service import parse_attachment_metadata, save_job_attachments

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _template_context(**extra: Any) -> dict[str, Any]:
    return {"app_title": APP_TITLE, **extra}


def _questions_from_form(
    question_text: List[str],
    question_notes: List[str],
    question_tags: List[str],
) -> List[QuestionCreate]:
    #Align parallel form lists into QuestionCreate objects (skip empty rows)
    payloads: List[QuestionCreate] = []
    for i, text in enumerate(question_text):
        if not text or not text.strip():
            continue
        notes_val = question_notes[i] if i < len(question_notes) else ""
        tags_val = question_tags[i] if i < len(question_tags) else ""
        notes = notes_val.strip() if notes_val and notes_val.strip() else None
        payloads.append(
            QuestionCreate(
                question_text=text.strip(),
                notes=notes,
                tags=question_service.parse_tags_csv(tags_val),
            )
        )
    return payloads


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return RedirectResponse(url="/jobs", status_code=302)


@router.get("/jobs/add", response_class=HTMLResponse, name="add_job_page")
def add_job_page(request: Request):
    return templates.TemplateResponse(request, "add_job.html", _template_context())


@router.post("/jobs/add")
async def add_job_submit(
    request: Request,
    role: str = Form(...),
    company_name: str = Form(...),
    location: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    workplace_type: Optional[str] = Form(None),
    current_stage: Optional[str] = Form(None),
    application_status: str = Form("Applied"),
    rejection_reason: Optional[str] = Form(None),
    recruiter_name: Optional[str] = Form(None),
    recruiter_email: Optional[str] = Form(None),
    comments: Optional[str] = Form(None),
    additional_attachments: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    payload = JobCreate(
        role=role,
        company_name=company_name,
        location=location,
        job_description=job_description,
        employment_type=employment_type or None,
        workplace_type=workplace_type or None,
        current_stage=current_stage or None,
        application_status=application_status,
        rejection_reason=rejection_reason,
        recruiter_name=recruiter_name,
        recruiter_email=recruiter_email or None,
        comments=comments,
    )
    # Links job to demo user via users table
    job = job_service.create_job(db, payload)

    metadata = await save_job_attachments(job.id, additional_attachments)
    if metadata:
        job.attachment_metadata = metadata
        db.commit()

    return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)


@router.get("/jobs", response_class=HTMLResponse, name="list_jobs_page")
def list_jobs_page(
    request: Request,
    company: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
):
    company_q = (company or "").strip()
    role_q = (role or "").strip()
    is_search = bool(company_q or role_q)

    if is_search:
        jobs = job_service.search_jobs(db, company=company_q or None, role=role_q or None)
    else:
        jobs = job_service.list_jobs(db)

    return templates.TemplateResponse(
        request,
        "list_jobs.html",
        _template_context(
            jobs=jobs,
            company=company_q,
            role=role_q,
            is_search=is_search,
        ),
    )


@router.get("/jobs/{job_id}", response_class=HTMLResponse, name="job_detail_page")
def job_detail_page(job_id: int, request: Request, db: Session = Depends(get_db)):
    job = (
        db.query(JobApplied)
        .options(
            joinedload(JobApplied.user),
            joinedload(JobApplied.interviews)
            .joinedload(Interview.questions)
            .joinedload(InterviewQuestion.tags),
        )
        .filter(JobApplied.id == job_id)
        .first()
    )
    if not job:
        return templates.TemplateResponse(
            request,
            "list_jobs.html",
            _template_context(jobs=[], error="Job not found"),
            status_code=404,
        )

    attachments = parse_attachment_metadata(job.attachment_metadata)
    return templates.TemplateResponse(
        request,
        "job_detail.html",
        _template_context(job=job, attachments=attachments),
    )


@router.get("/jobs/{job_id}/interviews/add", response_class=HTMLResponse)
def add_interview_page(job_id: int, request: Request, db: Session = Depends(get_db)):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        return RedirectResponse(url="/jobs", status_code=302)
    return templates.TemplateResponse(
        request,
        "add_interview.html",
        _template_context(job=job, today=date.today().isoformat()),
    )


@router.post("/jobs/{job_id}/interviews/add")
def add_interview_submit(
    job_id: int,
    round_number: int = Form(1),
    interview_date: Optional[str] = Form(None),
    interviewer_names: Optional[str] = Form(None),
    round_status: str = Form("Scheduled"),
    comments: Optional[str] = Form(None),
    question_text: List[str] = Form(default=[]),
    question_notes: List[str] = Form(default=[]),
    question_tags: List[str] = Form(default=[]),
    db: Session = Depends(get_db),
):
    job = job_service.get_job_or_none(db, job_id)
    if not job:
        return RedirectResponse(url="/jobs", status_code=302)

    parsed_date = date.fromisoformat(interview_date) if interview_date else None
    payload = InterviewCreate(
        round_number=round_number,
        interview_date=parsed_date,
        interviewer_names=interviewer_names,
        round_status=round_status,
        comments=comments,
    )
    interview = interview_service.create_interview(db, job, payload)

    question_payloads = _questions_from_form(question_text, question_notes, question_tags)
    if question_payloads:
        question_service.create_questions_for_interview(db, interview, question_payloads)

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


@router.get("/jobs/{job_id}/interviews/{interview_id}/questions/add", response_class=HTMLResponse)
def add_interview_questions_page(
    job_id: int,
    interview_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    job = job_service.get_job_or_none(db, job_id)
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not job or not interview or interview.job_id != job.id:
        return RedirectResponse(url=f"/jobs/{job_id}", status_code=302)
    return templates.TemplateResponse(
        request,
        "add_interview_questions.html",
        _template_context(job=job, interview=interview),
    )


@router.post("/jobs/{job_id}/interviews/{interview_id}/questions/add")
def add_interview_questions_submit(
    job_id: int,
    interview_id: int,
    question_text: List[str] = Form(default=[]),
    question_notes: List[str] = Form(default=[]),
    question_tags: List[str] = Form(default=[]),
    db: Session = Depends(get_db),
):
    job = job_service.get_job_or_none(db, job_id)
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not job or not interview or interview.job_id != job.id:
        return RedirectResponse(url="/jobs", status_code=302)

    question_payloads = _questions_from_form(question_text, question_notes, question_tags)
    if question_payloads:
        question_service.create_questions_for_interview(db, interview, question_payloads)

    return RedirectResponse(url=f"/jobs/{job_id}", status_code=303)


@router.get("/questions/search", response_class=HTMLResponse, name="search_questions_page")
def search_questions_page(
    request: Request,
    tags: Optional[str] = None,
    db: Session = Depends(get_db),
):
    results = []
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        questions = question_service.search_questions_by_tags(db, tag_list)
        results = [
            {
                "question": q.question_text,
                "notes": q.notes,
                "tags": ", ".join(t.name for t in q.tags),
                "interview_id": q.interview_id,
            }
            for q in questions
        ]
    return templates.TemplateResponse(
        request,
        "search_questions.html",
        _template_context(tags=tags or "", results=results),
    )

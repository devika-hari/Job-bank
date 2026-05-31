from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import not_found
from app.schemas.question import QuestionCreate, QuestionListResponse, QuestionResponse, QuestionUpdate
from app.services import interview_service, question_service
from app.utils import question_to_response

router = APIRouter(prefix="/api", tags=["Interview Questions"])


@router.get(
    "/interviews/{interview_id}/questions",
    response_model=QuestionListResponse,
    summary="List questions for an interview",
)
def list_questions(interview_id: int, db: Session = Depends(get_db)):
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not interview:
        raise not_found("Interview")
    items = question_service.list_questions_for_interview(db, interview_id)
    return QuestionListResponse(
        total=len(items),
        items=[question_to_response(q) for q in items],
    )


@router.post(
    "/interviews/{interview_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add interview question with tags",
)
def create_question(interview_id: int, payload: QuestionCreate, db: Session = Depends(get_db)):
    interview = interview_service.get_interview_or_none(db, interview_id)
    if not interview:
        raise not_found("Interview")
    question = question_service.create_question(db, interview, payload)
    return question_to_response(question)


@router.get("/questions/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = question_service.get_question_or_none(db, question_id)
    if not question:
        raise not_found("Question")
    return question_to_response(question)


@router.patch("/questions/{question_id}", response_model=QuestionResponse)
def update_question(question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)):
    question = question_service.get_question_or_none(db, question_id)
    if not question:
        raise not_found("Question")
    updated = question_service.update_question(db, question, payload)
    return question_to_response(updated)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = question_service.get_question_or_none(db, question_id)
    if not question:
        raise not_found("Question")
    question_service.delete_question(db, question)

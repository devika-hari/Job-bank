# =============================================================================
# Questions - Interview - Job Application business logic
# SQL query generation & execution
# =============================================================================
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.interview import Interview
from app.models.question import InterviewQuestion
from app.models.tag import Tag
from app.schemas.question import QuestionCreate, QuestionUpdate


def _normalize_tag_name(name: str) -> str:
    return name.strip()


def parse_tags_csv(tags_csv: Optional[str]) -> List[str]:
    """Turn 'Python, SQL, dbt' into ['Python', 'SQL', 'dbt']."""
    if not tags_csv:
        return []
    return [t.strip() for t in tags_csv.split(",") if t.strip()]


def _get_or_create_tags(db: Session, tag_names: List[str]) -> List[Tag]:
    tags: List[Tag] = []
    for raw in tag_names:
        name = _normalize_tag_name(raw)
        if not name:
            continue
        tag = db.query(Tag).filter(Tag.name.ilike(name)).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)
    return tags


def get_question_or_none(db: Session, question_id: int) -> Optional[InterviewQuestion]:
    return (
        db.query(InterviewQuestion)
        .options(joinedload(InterviewQuestion.tags))
        .filter(InterviewQuestion.id == question_id)
        .first()
    )


def list_questions_for_interview(db: Session, interview_id: int) -> List[InterviewQuestion]:
    return (
        db.query(InterviewQuestion)
        .options(joinedload(InterviewQuestion.tags))
        .filter(InterviewQuestion.interview_id == interview_id)
        .all()
    )


def create_question(db: Session, interview: Interview, payload: QuestionCreate) -> InterviewQuestion:
    question = InterviewQuestion(
        interview_id=interview.id,
        question_text=payload.question_text,
        notes=payload.notes,
    )
    question.tags = _get_or_create_tags(db, payload.tags)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def create_questions_for_interview(
    db: Session,
    interview: Interview,
    payloads: List[QuestionCreate],
) -> List[InterviewQuestion]:
    """
    Save multiple questions for one interview in a single database transaction.
    Used by the HTML interview form (optional question rows).
    """
    if not payloads:
        return []

    created: List[InterviewQuestion] = []
    for payload in payloads:
        question = InterviewQuestion(
            interview_id=interview.id,
            question_text=payload.question_text,
            notes=payload.notes,
        )
        question.tags = _get_or_create_tags(db, payload.tags)
        db.add(question)
        created.append(question)

    db.commit()
    for q in created:
        db.refresh(q)
    return created


def update_question(
    db: Session, question: InterviewQuestion, payload: QuestionUpdate
) -> InterviewQuestion:
    data = payload.model_dump(exclude_unset=True)
    tag_names = data.pop("tags", None)

    for field, value in data.items():
        setattr(question, field, value)

    if tag_names is not None:
        question.tags = _get_or_create_tags(db, tag_names)

    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question: InterviewQuestion) -> None:
    db.delete(question)
    db.commit()


def search_questions_by_tags(db: Session, tags: List[str]) -> List[InterviewQuestion]:
    normalized = [_normalize_tag_name(t) for t in tags if _normalize_tag_name(t)]
    if not normalized:
        return []

    query = (
        db.query(InterviewQuestion)
        .options(joinedload(InterviewQuestion.tags))
        .join(InterviewQuestion.tags)
        .filter(Tag.name.in_(normalized))
        .distinct()
    )
    return query.all()

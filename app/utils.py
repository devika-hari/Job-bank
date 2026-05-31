# =============================================================================
# Helper function to resolve Question - multiple tags
# =============================================================================

from app.models.question import InterviewQuestion
from app.schemas.question import QuestionResponse, TagResponse


def question_to_response(question: InterviewQuestion) -> QuestionResponse:
    # Map ORM question + tags to API response (tag names + tag_details)
    tag_details = [TagResponse.model_validate(t) for t in question.tags]
    return QuestionResponse(
        id=question.id,
        interview_id=question.interview_id,
        question_text=question.question_text,
        notes=question.notes,
        tags=[t.name for t in question.tags],
        tag_details=tag_details,
        created_at=question.created_at,
    )

"""
Search helpers including a small pandas example for learning.

pandas is NOT required for basic search — we use it to build tag statistics
that are easy to read in a table (good practice for data folks learning backend).
"""

from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from app.models.question import InterviewQuestion
from app.models.tag import Tag
from app.schemas.search import TagStatsResponse


def tag_question_stats(db: Session) -> List[TagStatsResponse]:
    """
    Count how many questions use each tag.

    Steps:
    1. Read tag + question ids from PostgreSQL via SQLAlchemy
    2. Build a pandas DataFrame
    3. groupby tag name and count distinct questions
    """
    rows = (
        db.query(Tag.name, InterviewQuestion.id.label("question_id"))
        .join(Tag.questions)
        .all()
    )

    if not rows:
        return []

    df = pd.DataFrame(rows, columns=["tag", "question_id"])
    grouped = df.groupby("tag")["question_id"].nunique().reset_index(name="question_count")

    return [
        TagStatsResponse(tag=row["tag"], question_count=int(row["question_count"]))
        for _, row in grouped.iterrows()
    ]

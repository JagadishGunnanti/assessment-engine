from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.exam_attempt import AttemptStatus


class StartExamRequest(BaseModel):
    learner_id: UUID


class ExamAttemptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exam_id: UUID
    learner_id: UUID
    status: AttemptStatus
    started_at: datetime
    submitted_at: datetime | None = None
    score: int | None = None


class ExamResultResponse(BaseModel):
    id: UUID
    exam_id: UUID
    learner_id: UUID
    status: AttemptStatus
    started_at: datetime
    submitted_at: datetime
    score: int
    total_questions: int
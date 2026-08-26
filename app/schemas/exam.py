from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import ExamQuestionResponse


class CreateExamRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    created_by: UUID


class ExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ExamDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    questions: list[ExamQuestionResponse]
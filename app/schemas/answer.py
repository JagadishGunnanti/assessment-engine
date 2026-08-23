from uuid import UUID

from pydantic import BaseModel, Field


class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    selected_option_ids: list[UUID] = Field(min_length=1)


class AnswerResponse(BaseModel):
    id: UUID
    attempt_id: UUID
    question_id: UUID
    selected_option_ids: list[UUID]
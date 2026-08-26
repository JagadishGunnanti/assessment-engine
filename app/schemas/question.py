from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateQuestionOptionRequest(BaseModel):
    text: str = Field(min_length=1)
    order: int = Field(ge=1)
    is_correct: bool


class CreateQuestionRequest(BaseModel):
    text: str = Field(min_length=1)
    order: int = Field(ge=1)
    options: list[CreateQuestionOptionRequest] = Field(min_length=2)


class QuestionOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    order: int
    is_correct: bool


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    exam_id: UUID
    text: str
    order: int
    options: list[QuestionOptionResponse]


class ExamQuestionOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    order: int


class ExamQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    order: int
    options: list[ExamQuestionOptionResponse]
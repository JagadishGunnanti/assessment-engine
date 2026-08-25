from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.attempt import ExamAttemptResponse, StartExamRequest
from app.schemas.exam import CreateExamRequest, ExamResponse
from app.schemas.question import CreateQuestionRequest, QuestionResponse
from app.services.exam import ExamService
from app.services.exam_attempt import ExamAttemptService
from app.services.question import QuestionService

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post(
    "",
    response_model=ExamResponse,
    status_code=201,
)
def create_exam(
    request: CreateExamRequest,
    db: Session = Depends(get_db),
) -> ExamResponse:
    service = ExamService(db)

    return service.create_exam(
        title=request.title,
        description=request.description,
        created_by=request.created_by,
    )


@router.post(
    "/{exam_id}/start",
    response_model=ExamAttemptResponse,
    status_code=201,
)
def start_exam(
    exam_id: UUID,
    request: StartExamRequest,
    db: Session = Depends(get_db),
) -> ExamAttemptResponse:
    service = ExamAttemptService(db)

    return service.start_exam(
        exam_id=exam_id,
        learner_id=request.learner_id,
    )

@router.post(
    "/{exam_id}/questions",
    response_model=QuestionResponse,
    status_code=201,
)
def create_question(
    exam_id: UUID,
    request: CreateQuestionRequest,
    db: Session = Depends(get_db),
) -> QuestionResponse:
    service = QuestionService(db)

    return service.create_question(
        exam_id=exam_id,
        text=request.text,
        order=request.order,
        options=[
            option.model_dump()
            for option in request.options
        ],
    )
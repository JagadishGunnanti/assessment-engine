from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.attempt import ExamAttemptResponse, StartExamRequest
from app.services.exam_attempt import ExamAttemptService

router = APIRouter(prefix="/exams", tags=["exams"])


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
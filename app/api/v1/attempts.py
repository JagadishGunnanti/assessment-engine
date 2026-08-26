from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.answer import SubmitAnswerRequest
from app.schemas.attempt import ExamAttemptResponse, ExamResultResponse
from app.services.answer import AnswerService
from app.services.exam_attempt import ExamAttemptService

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.post("/{attempt_id}/answers")
def submit_answer(
    attempt_id: UUID,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
):
    service = AnswerService(db)

    answer = service.submit_answer(
        attempt_id=attempt_id,
        question_id=request.question_id,
        option_ids=request.selected_option_ids,
    )

    return {
        "id": answer.id,
        "attempt_id": answer.attempt_id,
        "question_id": answer.question_id,
        "selected_option_ids": [
            option.question_option_id for option in answer.options
        ],
    }

@router.post(
    "/{attempt_id}/submit",
    response_model=ExamAttemptResponse,
)
def submit_exam(
    attempt_id: UUID,
    db: Session = Depends(get_db),
) -> ExamAttemptResponse:
    service = ExamAttemptService(db)

    return service.submit_exam(
        attempt_id=attempt_id,
    )

@router.get(
    "/{attempt_id}/result",
    response_model=ExamResultResponse,
)
def get_result(
    attempt_id: UUID,
    db: Session = Depends(get_db),
) -> ExamResultResponse:
    service = ExamAttemptService(db)

    attempt, total_questions = service.get_result(
        attempt_id=attempt_id,
    )

    return ExamResultResponse(
        id=attempt.id,
        exam_id=attempt.exam_id,
        learner_id=attempt.learner_id,
        status=attempt.status,
        started_at=attempt.started_at,
        submitted_at=attempt.submitted_at,
        score=attempt.score,
        total_questions=total_questions,
    )
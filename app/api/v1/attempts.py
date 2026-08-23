from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.answer import SubmitAnswerRequest
from app.services.answer import AnswerService

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
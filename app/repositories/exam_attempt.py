from uuid import UUID

from sqlalchemy.orm import Session

from app.models.exam_attempt import ExamAttempt


class ExamAttemptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        exam_id: UUID,
        learner_id: UUID,
    ) -> ExamAttempt:
        attempt = ExamAttempt(
            exam_id=exam_id,
            learner_id=learner_id,
        )

        self.db.add(attempt)
        self.db.flush()

        return attempt
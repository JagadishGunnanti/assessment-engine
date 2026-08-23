from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.exam_attempt import ExamAttempt
from app.models.user import User
from app.repositories.exam_attempt import ExamAttemptRepository


class ExamAttemptService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ExamAttemptRepository(db)

    def start_exam(
        self,
        *,
        exam_id: UUID,
        learner_id: UUID,
    ) -> ExamAttempt:
        exam = self.db.get(Exam, exam_id)

        if exam is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found",
            )

        learner = self.db.get(User, learner_id)

        if learner is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner not found",
            )

        attempt = self.repository.create(
            exam_id=exam_id,
            learner_id=learner_id,
        )

        self.db.commit()
        self.db.refresh(attempt)

        return attempt
from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.exam_attempt import AttemptStatus, ExamAttempt
from app.models.question import Question
from app.models.question_option import QuestionOption
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

    def submit_exam(
        self,
        *,
        attempt_id: UUID,
    ) -> ExamAttempt:
        attempt = self.db.get(ExamAttempt, attempt_id)

        if attempt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam attempt not found",
            )

        if attempt.status != AttemptStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Exam attempt has already been submitted",
            )

        attempt.score = self._calculate_score(attempt)
        attempt.status = AttemptStatus.SUBMITTED
        attempt.submitted_at = datetime.now(UTC)

        self.db.commit()
        self.db.refresh(attempt)

        return attempt

    def _calculate_score(self, attempt: ExamAttempt) -> int:
        score = 0

        for answer in attempt.answers:
            correct_option_ids = set(
                self.db.scalars(
                    select(QuestionOption.id).where(
                        QuestionOption.question_id == answer.question_id,
                        QuestionOption.is_correct.is_(True),
                    )
                ).all()
            )

            selected_option_ids = {
                option.question_option_id for option in answer.options
            }

            if selected_option_ids == correct_option_ids:
                score += 1

        return score

    def get_result(
        self,
        *,
        attempt_id: UUID,
    ) -> tuple[ExamAttempt, int]:
        attempt = self.db.get(ExamAttempt, attempt_id)

        if attempt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam attempt not found",
            )

        if attempt.status != AttemptStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Exam attempt has not been submitted",
            )

        total_questions = self.db.scalar(
            select(func.count(Question.id)).where(
                Question.exam_id == attempt.exam_id,
            )
        )

        return attempt, total_questions or 0
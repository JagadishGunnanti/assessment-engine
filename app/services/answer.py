from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.exam_attempt import AttemptStatus, ExamAttempt
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.repositories.answer import AnswerRepository


class AnswerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AnswerRepository(db)

    def submit_answer(
        self,
        *,
        attempt_id: UUID,
        question_id: UUID,
        option_ids: list[UUID],
    ) -> Answer:
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

        question = self.db.get(Question, question_id)

        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )

        if question.exam_id != attempt.exam_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question does not belong to this exam",
            )

        unique_option_ids = set(option_ids)

        if len(unique_option_ids) != len(option_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate option selected",
            )

        options = self.db.scalars(
            select(QuestionOption).where(
                QuestionOption.id.in_(unique_option_ids),
                QuestionOption.question_id == question_id,
            )
        ).all()

        if len(options) != len(unique_option_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more options do not belong to this question",
            )

        answer = self.repository.get_by_attempt_and_question(
            attempt_id=attempt_id,
            question_id=question_id,
        )

        if answer is None:
            answer = self.repository.create(
                attempt_id=attempt_id,
                question_id=question_id,
                option_ids=option_ids,
            )
        else:
            answer = self.repository.replace_options(
                answer=answer,
                option_ids=option_ids,
            )

        self.db.commit()
        self.db.refresh(answer)

        return answer
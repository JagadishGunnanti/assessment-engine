from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.question import Question
from app.repositories.question import QuestionRepository


class QuestionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = QuestionRepository(db)

    def create_question(
        self,
        *,
        exam_id: UUID,
        text: str,
        order: int,
        options: list[dict],
    ) -> Question:
        exam = self.db.get(Exam, exam_id)

        if exam is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found",
            )

        try:
            question = self.repository.create(
                exam_id=exam_id,
                text=text,
                order=order,
                options=options,
            )

            self.db.commit()
            self.db.refresh(question)

            return question

        except IntegrityError as exc:
            self.db.rollback()

            if "uq_questions_exam_order" in str(exc.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Question order already exists for this exam",
                ) from exc

            raise
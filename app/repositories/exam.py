from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.exam import Exam
from app.models.question import Question


class ExamRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        title: str,
        description: str | None,
        created_by: UUID,
    ) -> Exam:
        exam = Exam(
            title=title,
            description=description,
            created_by=created_by,
        )

        self.db.add(exam)
        self.db.flush()

        return exam

    def get_with_questions(
        self,
        *,
        exam_id: UUID,
    ) -> Exam | None:
        return self.db.scalar(
            select(Exam)
            .where(Exam.id == exam_id)
            .options(
                selectinload(Exam.questions).selectinload(
                    Question.options,
                ),
            )
        )
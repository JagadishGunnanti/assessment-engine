from uuid import UUID

from sqlalchemy.orm import Session

from app.models.exam import Exam


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
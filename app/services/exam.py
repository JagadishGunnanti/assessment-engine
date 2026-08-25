from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.user import User
from app.repositories.exam import ExamRepository


class ExamService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ExamRepository(db)

    def create_exam(
        self,
        *,
        title: str,
        description: str | None,
        created_by: UUID,
    ) -> Exam:
        creator = self.db.get(User, created_by)

        if creator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Creator not found",
            )

        exam = self.repository.create(
            title=title,
            description=description,
            created_by=created_by,
        )

        self.db.commit()
        self.db.refresh(exam)

        return exam
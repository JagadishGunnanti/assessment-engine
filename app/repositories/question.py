from uuid import UUID

from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.question_option import QuestionOption


class QuestionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        exam_id: UUID,
        text: str,
        order: int,
        options: list[dict],
    ) -> Question:
        question = Question(
            exam_id=exam_id,
            text=text,
            order=order,
        )

        self.db.add(question)
        self.db.flush()

        for option_data in options:
            self.db.add(
                QuestionOption(
                    question_id=question.id,
                    text=option_data["text"],
                    order=option_data["order"],
                    is_correct=option_data["is_correct"],
                )
            )

        self.db.flush()
        self.db.refresh(question)

        return question
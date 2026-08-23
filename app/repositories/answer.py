from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.answer_option import AnswerOption


class AnswerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_attempt_and_question(
        self,
        *,
        attempt_id: UUID,
        question_id: UUID,
    ) -> Answer | None:
        return self.db.scalar(
            select(Answer).where(
                Answer.attempt_id == attempt_id,
                Answer.question_id == question_id,
            )
        )

    def create(
        self,
        *,
        attempt_id: UUID,
        question_id: UUID,
        option_ids: list[UUID],
    ) -> Answer:
        answer = Answer(
            attempt_id=attempt_id,
            question_id=question_id,
        )

        self.db.add(answer)
        self.db.flush()

        for option_id in option_ids:
            self.db.add(
                AnswerOption(
                    answer_id=answer.id,
                    question_option_id=option_id,
                )
            )

        self.db.flush()

        return answer

    def replace_options(
        self,
        *,
        answer: Answer,
        option_ids: list[UUID],
    ) -> Answer:
        for option in list(answer.options):
            self.db.delete(option)

        self.db.flush()

        for option_id in option_ids:
            self.db.add(
                AnswerOption(
                    answer_id=answer.id,
                    question_option_id=option_id,
                )
            )

        self.db.flush()

        return answer
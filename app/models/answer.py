import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.answer_option import AnswerOption
    from app.models.exam_attempt import ExamAttempt
    from app.models.question import Question


class Answer(Base):
    __tablename__ = "answers"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            name="uq_answers_attempt_question",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id"),
        nullable=False,
    )

    attempt: Mapped["ExamAttempt"] = relationship(
        "ExamAttempt",
        back_populates="answers",
    )

    question: Mapped["Question"] = relationship(
        "Question",
    )

    options: Mapped[list["AnswerOption"]] = relationship(
        "AnswerOption",
        back_populates="answer",
        cascade="all, delete-orphan",
    )
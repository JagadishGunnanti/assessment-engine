import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.answer import Answer
    from app.models.question_option import QuestionOption


class AnswerOption(Base):
    __tablename__ = "answer_options"

    __table_args__ = (
        UniqueConstraint(
            "answer_id",
            "question_option_id",
            name="uq_answer_options_answer_option",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    answer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("answers.id", ondelete="CASCADE"),
        nullable=False,
    )

    question_option_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("question_options.id"),
        nullable=False,
    )

    answer: Mapped["Answer"] = relationship(
        "Answer",
        back_populates="options",
    )

    question_option: Mapped["QuestionOption"] = relationship(
        "QuestionOption",
    )
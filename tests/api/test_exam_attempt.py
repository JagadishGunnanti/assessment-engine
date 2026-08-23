import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.answer import Answer
from app.models.exam import Exam
from app.models.exam_attempt import ExamAttempt
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.user import User

client = TestClient(app)


def test_start_exam() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )

    db.add(learner)
    db.flush()

    exam = Exam(
        title="Test Exam",
        description="Integration test exam",
        created_by=learner.id,
    )

    db.add(exam)
    db.commit()
    db.refresh(exam)

    try:
        response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert response.status_code == 201

        data = response.json()

        assert data["exam_id"] == str(exam.id)
        assert data["learner_id"] == str(learner.id)
        assert data["status"] == "in_progress"
        assert data["started_at"] is not None
        assert data["id"] is not None

        attempt = db.get(ExamAttempt, uuid.UUID(data["id"]))

        assert attempt is not None
        assert attempt.exam_id == exam.id
        assert attempt.learner_id == learner.id

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()


def test_submit_answer() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )

    db.add(learner)
    db.flush()

    exam = Exam(
        title="MSQ Test Exam",
        description="Answer API integration test",
        created_by=learner.id,
    )

    db.add(exam)
    db.flush()

    question = Question(
        exam_id=exam.id,
        text="Which are AWS compute services?",
        order=1,
    )

    db.add(question)
    db.flush()

    options = [
        QuestionOption(
            question_id=question.id,
            text="EC2",
            order=1,
            is_correct=True,
        ),
        QuestionOption(
            question_id=question.id,
            text="S3",
            order=2,
            is_correct=False,
        ),
        QuestionOption(
            question_id=question.id,
            text="Lambda",
            order=3,
            is_correct=True,
        ),
        QuestionOption(
            question_id=question.id,
            text="RDS",
            order=4,
            is_correct=False,
        ),
    ]

    db.add_all(options)
    db.commit()

    try:
        start_response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert start_response.status_code == 201

        attempt_id = start_response.json()["id"]

        # First answer: EC2 + Lambda.
        answer_response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question.id),
                "selected_option_ids": [
                    str(options[0].id),
                    str(options[2].id),
                ],
            },
        )

        assert answer_response.status_code == 200

        data = answer_response.json()

        assert data["attempt_id"] == attempt_id
        assert data["question_id"] == str(question.id)
        assert set(data["selected_option_ids"]) == {
            str(options[0].id),
            str(options[2].id),
        }

        # Second answer: S3 + Lambda.
        # This should replace the previous selection.
        replacement_response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question.id),
                "selected_option_ids": [
                    str(options[1].id),
                    str(options[2].id),
                ],
            },
        )

        assert replacement_response.status_code == 200

        replacement_data = replacement_response.json()

        # Same Answer record should be updated.
        assert replacement_data["id"] == data["id"]

        assert set(replacement_data["selected_option_ids"]) == {
            str(options[1].id),
            str(options[2].id),
        }

        # Verify there is still only one Answer for this question.
        answer = db.get(Answer, uuid.UUID(data["id"]))

        assert answer is not None
        assert answer.attempt_id == uuid.UUID(attempt_id)
        assert answer.question_id == question.id

        db.refresh(answer)

        assert len(answer.options) == 2
        assert {
            option.question_option_id for option in answer.options
        } == {
            options[1].id,
            options[2].id,
        }

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()
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


def test_submit_answer_rejects_option_from_different_question() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Validation Test Exam",
        created_by=learner.id,
    )
    db.add(exam)
    db.flush()

    question = Question(
        exam_id=exam.id,
        text="Question 1",
        order=1,
    )
    other_question = Question(
        exam_id=exam.id,
        text="Question 2",
        order=2,
    )
    db.add_all([question, other_question])
    db.flush()

    valid_option = QuestionOption(
        question_id=question.id,
        text="Valid option",
        order=1,
        is_correct=True,
    )
    other_option = QuestionOption(
        question_id=other_question.id,
        text="Option from another question",
        order=1,
        is_correct=True,
    )

    db.add_all([valid_option, other_option])
    db.commit()

    try:
        start_response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert start_response.status_code == 201

        attempt_id = start_response.json()["id"]

        response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question.id),
                "selected_option_ids": [str(other_option.id)],
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "One or more options do not belong to this question"
        )

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()


def test_submit_answer_rejects_question_from_different_exam() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Exam A",
        description="First exam",
        created_by=learner.id,
    )
    other_exam = Exam(
        title="Exam B",
        description="Second exam",
        created_by=learner.id,
    )
    db.add_all([exam, other_exam])
    db.flush()

    question = Question(
    exam_id=other_exam.id,
    text="Question from another exam",
    order=1,
)

    db.add(question)
    db.flush()

    option = QuestionOption(
        question_id=question.id,
        text="Option from another exam",
        order=1,
        is_correct=True,
    )

    db.add(option)
    db.commit()

    try:
        # Start an attempt for Exam A.
        start_response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert start_response.status_code == 201

        attempt_id = start_response.json()["id"]

        # Try answering a question that belongs to Exam B.
        response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question.id),
                "selected_option_ids": [str(option.id)],
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Question does not belong to this exam"
        )

    finally:
        db.delete(exam)
        db.delete(other_exam)
        db.delete(learner)
        db.commit()
        db.close()


def test_submit_answer_rejects_duplicate_options() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Duplicate Option Test",
        created_by=learner.id,
    )
    db.add(exam)
    db.flush()

    question = Question(
        exam_id=exam.id,
        text="Select the correct option",
        order=1,
    )
    db.add(question)
    db.flush()

    option = QuestionOption(
        question_id=question.id,
        text="Correct option",
        order=1,
        is_correct=True,
    )
    db.add(option)
    db.commit()

    try:
        start_response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert start_response.status_code == 201

        attempt_id = start_response.json()["id"]

        response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question.id),
                "selected_option_ids": [
                    str(option.id),
                    str(option.id),
                ],
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Duplicate option selected"

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()

def test_submit_exam() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Submit Test Exam",
        created_by=learner.id,
    )
    db.add(exam)
    db.commit()

    try:
        start_response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert start_response.status_code == 201

        attempt_id = start_response.json()["id"]

        response = client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == attempt_id
        assert data["exam_id"] == str(exam.id)
        assert data["learner_id"] == str(learner.id)
        assert data["status"] == "submitted"
        assert data["submitted_at"] is not None

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()

def test_submit_exam_rejects_second_submission() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Double Submit Test",
        created_by=learner.id,
    )
    db.add(exam)
    db.commit()

    try:
        start_response = client.post(
            f"/api/v1/exams/{exam.id}/start",
            json={"learner_id": str(learner.id)},
        )

        assert start_response.status_code == 201

        attempt_id = start_response.json()["id"]

        first_response = client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
        )

        assert first_response.status_code == 200

        second_response = client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
        )

        assert second_response.status_code == 409
        assert second_response.json()["detail"] == (
            "Exam attempt has already been submitted"
        )

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()

def test_submit_exam_calculates_score_for_correct_msq() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="MSQ Scoring Test",
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

        submit_response = client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
        )

        assert submit_response.status_code == 200

        data = submit_response.json()

        assert data["status"] == "submitted"
        assert data["score"] == 1

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()

def test_submit_exam_calculates_zero_for_incorrect_msq() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Incorrect MSQ Scoring Test",
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

        # EC2 + S3 is incorrect because Lambda is also required.
        answer_response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question.id),
                "selected_option_ids": [
                    str(options[0].id),
                    str(options[1].id),
                ],
            },
        )

        assert answer_response.status_code == 200

        submit_response = client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
        )

        assert submit_response.status_code == 200

        data = submit_response.json()

        assert data["status"] == "submitted"
        assert data["score"] == 0

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()

def test_submit_exam_calculates_score_for_multiple_questions() -> None:
    db = SessionLocal()

    learner = User(
        name="Test Learner",
        email=f"learner-{uuid.uuid4()}@example.com",
    )
    db.add(learner)
    db.flush()

    exam = Exam(
        title="Multiple Question Scoring Test",
        created_by=learner.id,
    )
    db.add(exam)
    db.flush()

    question_one = Question(
        exam_id=exam.id,
        text="Which are AWS compute services?",
        order=1,
    )
    question_two = Question(
        exam_id=exam.id,
        text="Which are AWS storage services?",
        order=2,
    )
    question_three = Question(
        exam_id=exam.id,
        text="Which are AWS database services?",
        order=3,
    )

    db.add_all([question_one, question_two, question_three])
    db.flush()

    options = [
        # Question 1: EC2 + Lambda are correct.
        QuestionOption(
            question_id=question_one.id,
            text="EC2",
            order=1,
            is_correct=True,
        ),
        QuestionOption(
            question_id=question_one.id,
            text="S3",
            order=2,
            is_correct=False,
        ),
        QuestionOption(
            question_id=question_one.id,
            text="Lambda",
            order=3,
            is_correct=True,
        ),
        # Question 2: S3 is correct.
        QuestionOption(
            question_id=question_two.id,
            text="S3",
            order=1,
            is_correct=True,
        ),
        QuestionOption(
            question_id=question_two.id,
            text="EC2",
            order=2,
            is_correct=False,
        ),
        # Question 3: RDS is correct.
        QuestionOption(
            question_id=question_three.id,
            text="RDS",
            order=1,
            is_correct=True,
        ),
        QuestionOption(
            question_id=question_three.id,
            text="Lambda",
            order=2,
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

        # Question 1: correct → +1.
        response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question_one.id),
                "selected_option_ids": [
                    str(options[0].id),
                    str(options[2].id),
                ],
            },
        )
        assert response.status_code == 200

        # Question 2: incorrect → +0.
        response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question_two.id),
                "selected_option_ids": [str(options[4].id)],
            },
        )
        assert response.status_code == 200

        # Question 3: correct → +1.
        response = client.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": str(question_three.id),
                "selected_option_ids": [str(options[5].id)],
            },
        )
        assert response.status_code == 200

        submit_response = client.post(
            f"/api/v1/attempts/{attempt_id}/submit",
        )

        assert submit_response.status_code == 200

        data = submit_response.json()

        assert data["status"] == "submitted"
        assert data["score"] == 2

    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()
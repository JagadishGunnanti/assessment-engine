import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models.exam import Exam
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
        from app.models.exam_attempt import ExamAttempt
        attempt = db.get(ExamAttempt, uuid.UUID(data["id"]))
        assert attempt is not None
        assert attempt.exam_id == exam.id
        assert attempt.learner_id == learner.id



    finally:
        db.delete(exam)
        db.delete(learner)
        db.commit()
        db.close()
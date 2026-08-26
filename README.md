# Assessment Engine

Backend engine for creating, conducting, and evaluating online assessments.

The application provides APIs for creating exams, adding MSQ (Multiple Select Questions), starting exam attempts, submitting answers, evaluating attempts, and retrieving results.

## Features

- Create exams and MSQ questions
- Start and manage exam attempts
- Submit and update answers
- Validate questions and selected options
- Submit exams and calculate scores
- Retrieve exams and results
- Prevent exposing correct answers to learners
- PostgreSQL database with SQLAlchemy
- Alembic database migrations
- API integration tests
- Ruff code-quality checks

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Pytest
- Ruff
- Docker / Docker Compose

## Architecture

```text
API
 │
 ▼
Service
 │
 ▼
Repository
 │
 ▼
PostgreSQL
```

### Layers

- **API** — HTTP endpoints and request/response handling
- **Schemas** — Pydantic request/response models
- **Services** — Business logic and validation
- **Repositories** — Database access
- **Models** — SQLAlchemy database models

## Project Structure

```text
assessment-engine/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── cache/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── alembic/
│   └── versions/
├── tests/
│   └── api/
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Setup

### Prerequisites

- Python 3.13
- Docker
- Docker Compose
- PostgreSQL

### 1. Create the virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Configure the PostgreSQL connection in `.env`.

### 4. Start PostgreSQL

```bash
docker compose up -d
```

### 5. Run database migrations

```bash
alembic upgrade head
```

## Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

## API Endpoints

### Exams

```text
POST /api/v1/exams
GET  /api/v1/exams/{exam_id}
```

### Questions

```text
POST /api/v1/exams/{exam_id}/questions
```

### Exam Attempts

```text
POST /api/v1/exams/{exam_id}/start
POST /api/v1/attempts/{attempt_id}/answers
POST /api/v1/attempts/{attempt_id}/submit
GET  /api/v1/attempts/{attempt_id}/result
```

### Health Check

```text
GET /health
```

## MSQ Scoring

A question receives **1 point only when the selected options exactly match the correct options**.

For example:

```text
Correct options: EC2 + Lambda

EC2 + Lambda  → 1 point
EC2           → 0 points
Lambda        → 0 points
EC2 + S3      → 0 points
```

The final exam score is the number of questions answered completely correctly.

## Validation

The application validates:

- Exam and learner existence
- Question and option ownership
- Duplicate option selections
- Duplicate question ordering
- Duplicate option ordering
- Exam attempt status
- Duplicate exam submissions

Invalid operations return appropriate HTTP error responses.

## Database Migrations

Apply migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

## Testing

Run the complete test suite:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run Ruff:

```bash
ruff check app tests
```

Current status:

```text
20 tests passed
Ruff checks passed
```

## Future Improvements

- Authentication and authorization
- Instructor and learner roles
- Exam timers and automatic submission
- Attempt limits
- Exam scheduling
- Redis caching
- Rate limiting
- CI/CD pipeline
- AWS deployment
- Monitoring and observability
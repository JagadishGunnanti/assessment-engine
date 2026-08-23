from fastapi import FastAPI

from app.api.v1.attempts import router as attempts_router
from app.api.v1.exams import router as exams_router

app = FastAPI(
    title="Assessment Engine",
    description="Backend engine for creating, conducting, and evaluating online assessments.",
    version="0.1.0",
)

app.include_router(
    exams_router,
    prefix="/api/v1",
)

app.include_router(
    attempts_router,
    prefix="/api/v1",
)



@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
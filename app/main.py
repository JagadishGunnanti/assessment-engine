from fastapi import FastAPI

app = FastAPI(
    title="Assessment Engine",
    description="Backend engine for creating, conducting, and evaluating online assessments.",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
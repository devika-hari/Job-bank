# =============================================================================
# My Job Bank App
# Run locally:  uvicorn app.main:app --reload

# - HTML UI: http://127.0.0.1:8000/jobs
# - Swagger: http://127.0.0.1:8000/docs
# =============================================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import APP_TITLE, UPLOAD_DIR
from app.database import SessionLocal, init_db, seed_default_user
from app.routers import interviews, jobs, pages, questions, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup / shutdown hooks
    # On startup we create tables and seed a demo user
    init_db()
    db = SessionLocal()
    try:
        seed_default_user(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=APP_TITLE,
    description=(
        "App to track job applications, interviews, and questions. "
        "Open /docs for interactive Swagger documentation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    # Return clear 422 errors when Pydantic validation fails
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Validation failed — check your request body or query params"},
    )


# Register routers
app.include_router(jobs.router)
app.include_router(interviews.router)
app.include_router(questions.router)
app.include_router(search.router)
app.include_router(pages.router)

# Uploaded documents (resumes, cover letters, etc.)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/health", tags=["Health"])
def health_check():
    #Simple endpoint for checks
    return {"status": "ok", "app": APP_TITLE}

from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models import Base, Learner, Course
from src.mastery import calculate_skill_mastery
from src.recommender import generate_recommendations
from src.learning_paths import (
    create_learning_path,
    get_learning_path_content,
)

# Locate the project root independently of the terminal directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "learning_dev.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

app = FastAPI(
    title="AI-Powered Personalized Learning Recommendation System",
    description=(
        "API for learner mastery, personalized recommendations, "
        "and learning paths."
    ),
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Learning Recommendation API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/learners/{learner_id}/mastery")
def learner_mastery(
    learner_id: str,
    db: Session = Depends(get_db),
):
    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise HTTPException(
            status_code=404,
            detail="Learner not found",
        )

    if learner.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Learner is not active",
        )

    try:
        mastery = calculate_skill_mastery(db, learner_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "learner_id": learner_id,
        "skills": mastery,
    }


@app.get("/learners/{learner_id}/recommendations")
def learner_recommendations(
    learner_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise HTTPException(
            status_code=404,
            detail="Learner not found",
        )

    if learner.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Learner is not active",
        )

    recommendations = generate_recommendations(
        db,
        learner_id,
        limit=limit,
    )

    return {
        "learner_id": learner_id,
        "total": len(recommendations),
        "recommendations": recommendations,
    }


@app.post("/learners/{learner_id}/learning-paths")
def create_path(
    learner_id: str,
    course_id: str,
    db: Session = Depends(get_db),
):
    try:
        path = create_learning_path(
            db,
            learner_id,
            course_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "learning_path_id": path.learning_path_id,
        "learner_id": path.learner_id,
        "course_id": path.course_id,
        "status": path.status,
        "version": path.version,
    }


@app.get("/learners/{learner_id}/courses/{course_id}/learning-content")
def learning_path_content(
    learner_id: str,
    course_id: str,
    db: Session = Depends(get_db),
):
    try:
        content = get_learning_path_content(
            db,
            learner_id,
            course_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "learner_id": learner_id,
        "course_id": course_id,
        "total": len(content),
        "content": content,
    }


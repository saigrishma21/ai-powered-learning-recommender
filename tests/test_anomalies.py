
import os
import sys
import pytest

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

from src.models import (
    Base,
    Learner,
    Course,
    ContentItem,
    Attempt,
    AssessmentResult,
)

DATABASE_URL = "sqlite:///./learning_dev.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_all_attempts_have_assessment_results(db):
    attempts_without_results = (
        db.query(Attempt)
        .outerjoin(
            AssessmentResult,
            Attempt.attempt_id == AssessmentResult.attempt_id,
        )
        .filter(AssessmentResult.result_id.is_(None))
        .count()
    )

    assert attempts_without_results == 0


def test_assessment_scores_are_valid(db):
    invalid_scores = (
        db.query(AssessmentResult)
        .filter(
            (AssessmentResult.percentage < 0)
            | (AssessmentResult.percentage > 100)
            | (AssessmentResult.score < 0)
            | (AssessmentResult.max_score <= 0)
            | (AssessmentResult.score > AssessmentResult.max_score)
        )
        .count()
    )

    assert invalid_scores == 0


def test_attempts_reference_existing_learners_and_content(db):
    invalid_attempts = (
        db.query(Attempt)
        .outerjoin(
            Learner,
            Attempt.learner_id == Learner.learner_id,
        )
        .outerjoin(
            ContentItem,
            Attempt.content_id == ContentItem.content_id,
        )
        .filter(
            (Learner.learner_id.is_(None))
            | (ContentItem.content_id.is_(None))
        )
        .count()
    )

    assert invalid_attempts == 0


def test_published_content_exists(db):
    published_count = (
        db.query(func.count(ContentItem.content_id))
        .filter(ContentItem.status == "PUBLISHED")
        .scalar()
    )

    assert published_count > 0


def test_attempts_have_valid_timestamps(db):
    invalid_timestamps = (
        db.query(Attempt)
        .filter(
            Attempt.completed_at.is_(None)
            | (Attempt.completed_at < Attempt.started_at)
        )
        .count()
    )

    assert invalid_timestamps == 0


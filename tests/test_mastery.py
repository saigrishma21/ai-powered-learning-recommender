from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
from src.models import (
    Learner,
    Course,
    Skill,
    ContentItem,
    ContentSkill,
    Attempt,
    AssessmentResult,
)
from src.mastery import calculate_skill_mastery


@pytest.fixture
def db():
    """Create an isolated in-memory database for each test."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    session = TestingSessionLocal()

    try:
        learner = Learner(
            learner_id="LRN-TEST-001",
            name="Test Learner",
            email="mastery-test@example.com",
            status="ACTIVE",
            created_at=datetime(2026, 1, 1),
        )

        course = Course(
            course_id="CRS-TEST-001",
            title="Python Programming",
            description="Test course",
            status="PUBLISHED",
            created_at=datetime(2026, 1, 1),
        )

        skill = Skill(
            skill_id="SKL-TEST-001",
            skill_name="Python Basics",
            description="Test skill",
            status="ACTIVE",
            created_at=datetime(2026, 1, 1),
        )

        content = ContentItem(
            content_id="CNT-TEST-001",
            course_id="CRS-TEST-001",
            title="Python Basics Assessment",
            content_type="QUIZ",
            difficulty="BEGINNER",
            estimated_minutes=10,
            status="PUBLISHED",
            created_at=datetime(2026, 1, 1),
        )

        session.add_all([
            learner,
            course,
            skill,
            content,
        ])
        session.flush()

        mapping = ContentSkill(
            content_skill_id=1,
            content_id="CNT-TEST-001",
            skill_id="SKL-TEST-001",
            contribution_weight=1.0,
        )

        session.add(mapping)
        session.flush()

        # Assessment 1: 40% on January 10.
        attempt1 = Attempt(
            attempt_id="ATT-LRN-TEST-001-000001",
            learner_id="LRN-TEST-001",
            content_id="CNT-TEST-001",
            attempt_number=1,
            started_at=datetime(2026, 1, 10, 9, 0),
            completed_at=datetime(2026, 1, 10, 10, 0),
            status="COMPLETED",
        )

        session.add(attempt1)
        session.flush()

        result1 = AssessmentResult(
            result_id="RES-TEST-001",
            attempt_id=attempt1.attempt_id,
            score=40,
            max_score=100,
            percentage=40,
            passed=False,
            assessed_at=datetime(2026, 1, 10, 10, 0),
        )

        # Assessment 2: 100% on January 20.
        # This result must not affect mastery as of January 15.
        attempt2 = Attempt(
            attempt_id="ATT-LRN-TEST-001-000002",
            learner_id="LRN-TEST-001",
            content_id="CNT-TEST-001",
            attempt_number=2,
            started_at=datetime(2026, 1, 20, 9, 0),
            completed_at=datetime(2026, 1, 20, 10, 0),
            status="COMPLETED",
        )

        session.add(attempt2)
        session.flush()

        result2 = AssessmentResult(
            result_id="RES-TEST-002",
            attempt_id=attempt2.attempt_id,
            score=100,
            max_score=100,
            percentage=100,
            passed=True,
            assessed_at=datetime(2026, 1, 20, 10, 0),
        )

        session.add_all([result1, result2])
        session.commit()

        yield session

    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_future_assessment_is_excluded_from_historical_mastery(db):
    """Future scores must not affect an earlier mastery calculation."""

    mastery = calculate_skill_mastery(
        db,
        "LRN-TEST-001",
        as_of=datetime(2026, 1, 15, 23, 59),
    )

    skill_mastery = mastery["SKL-TEST-001"]

    assert skill_mastery["assessment_count"] == 1
    assert skill_mastery["mastery_score"] == 40.0


def test_all_assessments_are_used_without_cutoff(db):
    """Without an as_of cutoff, both available assessments are used."""

    mastery = calculate_skill_mastery(
        db,
        "LRN-TEST-001",
    )

    skill_mastery = mastery["SKL-TEST-001"]

    assert skill_mastery["assessment_count"] == 2

    # The more recent observation receives greater weight:
    # (40 * 1 + 100 * 2) / (1 + 2) = 80.
    assert skill_mastery["mastery_score"] == 80.0


def test_unknown_learner_raises_error(db):
    """An unknown learner should produce a clear error."""

    with pytest.raises(ValueError, match="Learner not found"):
        calculate_skill_mastery(
            db,
            "LRN-UNKNOWN",
        )


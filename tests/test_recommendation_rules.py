import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models import (
    Base,
    Learner,
    Course,
    Skill,
    ContentItem,
    ContentSkill,
)
from src.recommender import generate_recommendations


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    learner = Learner(
        learner_id="LRN-TEST-001",
        name="Test Learner",
        email="test@example.com",
        status="ACTIVE",
    )

    inactive_learner = Learner(
        learner_id="LRN-TEST-002",
        name="Inactive Learner",
        email="inactive@example.com",
        status="INACTIVE",
    )

    course = Course(
        course_id="CRS-TEST-001",
        title="Python Fundamentals",
        description="Python basics for beginners",
        status="PUBLISHED",
    )

    skill = Skill(
        skill_id="SKL-TEST-001",
        skill_name="Python Basics",
        description="Fundamental Python programming",
        status="ACTIVE",
    )

    session.add_all([
        learner,
        inactive_learner,
        course,
        skill,
    ])
    session.flush()

    beginner_content = ContentItem(
        content_id="CNT-TEST-001",
        course_id=course.course_id,
        title="Python Introduction",
        content_type="VIDEO",
        difficulty="BEGINNER",
        estimated_minutes=15,
        status="PUBLISHED",
    )

    archived_content = ContentItem(
        content_id="CNT-TEST-002",
        course_id=course.course_id,
        title="Archived Python Lesson",
        content_type="ARTICLE",
        difficulty="BEGINNER",
        estimated_minutes=10,
        status="ARCHIVED",
    )

    session.add_all([beginner_content, archived_content])
    session.flush()

    session.add_all([
        ContentSkill(
            content_id=beginner_content.content_id,
            skill_id=skill.skill_id,
            contribution_weight=1.0,
        ),
        ContentSkill(
            content_id=archived_content.content_id,
            skill_id=skill.skill_id,
            contribution_weight=1.0,
        ),
    ])

    session.commit()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_inactive_learner_gets_no_recommendations(db):
    recommendations = generate_recommendations(
        db,
        "LRN-TEST-002",
    )

    assert recommendations == []


def test_archived_content_is_not_recommended(db):
    recommendations = generate_recommendations(
        db,
        "LRN-TEST-001",
    )

    recommended_ids = {
        item["content_id"] for item in recommendations
    }

    assert "CNT-TEST-002" not in recommended_ids


def test_active_learner_can_receive_published_content(db):
    recommendations = generate_recommendations(
        db,
        "LRN-TEST-001",
    )

    recommended_ids = {
        item["content_id"] for item in recommendations
    }

    assert "CNT-TEST-001" in recommended_ids


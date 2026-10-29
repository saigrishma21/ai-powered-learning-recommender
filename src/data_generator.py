import random
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy.orm import Session

from config.settings import (
    SEED,
    NUM_LEARNERS,
    NUM_COURSES,
    NUM_SKILLS,
    NUM_CONTENT_ITEMS,
    NUM_ATTEMPTS,
    MAX_SCORE,
    PASSING_THRESHOLD,
)

from src.models import (
    Learner,
    Course,
    Skill,
    SkillPrerequisite,
    ContentItem,
    ContentSkill,
    Attempt,
    AssessmentResult,
)


def generate_id(prefix: str, number: int) -> str:
    """Generate deterministic IDs."""
    return f"{prefix}-{number:06d}"


def generate_master_data(db: Session) -> None:
    """Generate learners, courses, skills, prerequisites and content."""

    random.seed(SEED)
    rng = np.random.default_rng(SEED)

    # Prevent duplicate master-data generation.
    if db.query(Learner).first():
        raise ValueError(
            "Master data already exists. "
            "Use a fresh development database."
        )

    now = datetime(2026, 10, 22, 12, 0, 0)

    # --------------------------------------------------
    # 1. Generate courses
    # --------------------------------------------------

    course_names = [
        "Python Programming",
        "Web Development",
        "Data Science",
        "Machine Learning",
        "Artificial Intelligence",
        "Database Management",
        "Cloud Computing",
        "Cybersecurity",
        "Software Engineering",
        "C++ Programming",
    ]

    courses = []

    for i in range(1, NUM_COURSES + 1):
        course = Course(
            course_id=generate_id("CRS", i),
            title=course_names[(i - 1) % len(course_names)],
            description=f"Learning course number {i}",
            status="PUBLISHED",
            created_at=now - timedelta(
                days=int(rng.integers(30, 501))
            ),
        )
        courses.append(course)

    db.add_all(courses)
    db.flush()

    # --------------------------------------------------
    # 2. Generate learners
    # --------------------------------------------------

    learners = []

    for i in range(1, NUM_LEARNERS + 1):
        learner = Learner(
            learner_id=generate_id("LRN", i),
            name=f"Learner {i:04d}",
            email=f"learner{i:04d}@example.com",
            status="ACTIVE",
            created_at=now - timedelta(
                days=int(rng.integers(1, 366))
            ),
        )
        learners.append(learner)

    db.add_all(learners)
    db.flush()

    # --------------------------------------------------
    # 3. Generate skills
    # --------------------------------------------------

    skills = []

    for i in range(1, NUM_SKILLS + 1):
        skill = Skill(
            skill_id=generate_id("SKL", i),
            skill_name=f"Skill {i:03d}",
            description=f"Description for skill {i}",
            status="ACTIVE",
            created_at=now - timedelta(
                days=int(rng.integers(30, 501))
            ),
        )
        skills.append(skill)

    db.add_all(skills)
    db.flush()

    # --------------------------------------------------
    # 4. Generate skill prerequisites
    # --------------------------------------------------

    prerequisites = []

    for i in range(2, NUM_SKILLS + 1):
        prerequisite = SkillPrerequisite(
            skill_id=generate_id("SKL", i),
            prerequisite_skill_id=generate_id("SKL", i - 1),
            effective_from=now - timedelta(days=30),
            effective_to=None,
            status="ACTIVE",
        )
        prerequisites.append(prerequisite)

    db.add_all(prerequisites)
    db.flush()

    # --------------------------------------------------
    # 5. Generate content items
    # --------------------------------------------------

    content_types = [
        "VIDEO",
        "ARTICLE",
        "QUIZ",
        "EXERCISE",
        "PROJECT",
    ]

    difficulties = [
        "BEGINNER",
        "INTERMEDIATE",
        "ADVANCED",
    ]

    content_items = []

    for i in range(1, NUM_CONTENT_ITEMS + 1):
        course_number = ((i - 1) % NUM_COURSES) + 1

        content = ContentItem(
            content_id=generate_id("CNT", i),
            course_id=generate_id("CRS", course_number),
            title=f"Learning Activity {i:04d}",
            content_type=content_types[
                (i - 1) % len(content_types)
            ],
            difficulty=difficulties[
                (i - 1) % len(difficulties)
            ],
            estimated_minutes=int(rng.integers(5, 61)),
            status="PUBLISHED",
            created_at=now - timedelta(
                days=int(rng.integers(1, 301))
            ),
        )
        content_items.append(content)

    db.add_all(content_items)
    db.flush()

    # --------------------------------------------------
    # 6. Map content items to skills
    # --------------------------------------------------

    content_skills = []

    for i in range(1, NUM_CONTENT_ITEMS + 1):
        skill_number = ((i - 1) % NUM_SKILLS) + 1

        content_skill = ContentSkill(
            content_skill_id=i,
            content_id=generate_id("CNT", i),
            skill_id=generate_id("SKL", skill_number),
            contribution_weight=1.0,
        )
        content_skills.append(content_skill)

    db.add_all(content_skills)
    db.commit()

    print("\nMaster data generated successfully!")
    print(f"Learners: {len(learners)}")
    print(f"Courses: {len(courses)}")
    print(f"Skills: {len(skills)}")
    print(f"Skill prerequisites: {len(prerequisites)}")
    print(f"Content items: {len(content_items)}")
    print(f"Content-skill mappings: {len(content_skills)}")


def generate_attempts(db: Session) -> None:
    """Generate attempts and assessment results deterministically."""

    rng = np.random.default_rng(SEED + 1)

    learners = (
        db.query(Learner)
        .order_by(Learner.learner_id)
        .all()
    )

    content_items = (
        db.query(ContentItem)
        .order_by(ContentItem.content_id)
        .all()
    )

    if not learners or not content_items:
        raise ValueError(
            "Generate master data before generating attempts."
        )

    if db.query(Attempt).first():
        raise ValueError(
            "Attempts already exist. "
            "Use a fresh development database."
        )

    reference_time = datetime(2026, 10, 22, 12, 0, 0)

    # Tracks attempt number and latest completion time
    # for each learner-content pair.
    pair_history = {}

    # Separately tracks the unique attempt ID sequence
    # for each learner.
    learner_attempt_counts = {}

    attempts = []
    results = []

    for i in range(1, NUM_ATTEMPTS + 1):

        learner = learners[
            int(rng.integers(0, len(learners)))
        ]

        content = content_items[
            int(rng.integers(0, len(content_items)))
        ]

        pair = (
            learner.learner_id,
            content.content_id,
        )

        history = pair_history.get(pair)

        if history is None:
            attempt_number = 1

            days_ago = int(rng.integers(1, 365))

            started_at = reference_time - timedelta(
                days=days_ago,
                minutes=int(rng.integers(0, 1440)),
            )
        else:
            attempt_number = history["attempt_number"] + 1

            started_at = history["completed_at"] + timedelta(
                minutes=int(rng.integers(1, 1441))
            )

        duration_minutes = int(rng.integers(1, 121))

        completed_at = started_at + timedelta(
            minutes=duration_minutes
        )

        pair_history[pair] = {
            "attempt_number": attempt_number,
            "completed_at": completed_at,
        }

        # Generate assessment score.
        max_score = float(MAX_SCORE)

        score = float(
            rng.integers(0, int(max_score) + 1)
        )

        percentage = round(
            (score / max_score) * 100,
            2,
        )

        passed = percentage >= PASSING_THRESHOLD

        # Generate a unique, sequential ID for this learner.
        learner_attempt_counts[learner.learner_id] = (
            learner_attempt_counts.get(learner.learner_id, 0) + 1
        )

        attempt_id = (
            f"ATT-{learner.learner_id}-"
            f"{learner_attempt_counts[learner.learner_id]:06d}"
        )

        result_id = generate_id("RES", i)

        attempt = Attempt(
            attempt_id=attempt_id,
            learner_id=learner.learner_id,
            content_id=content.content_id,
            attempt_number=attempt_number,
            started_at=started_at,
            completed_at=completed_at,
            status="COMPLETED",
        )

        result = AssessmentResult(
            result_id=result_id,
            attempt_id=attempt_id,
            score=score,
            max_score=max_score,
            percentage=percentage,
            passed=passed,
            assessed_at=completed_at,
        )

        attempts.append(attempt)
        results.append(result)

        # Insert batches in foreign-key-safe order.
        if len(attempts) >= 1000:
            db.add_all(attempts)
            db.flush()

            db.add_all(results)
            db.flush()

            attempts.clear()
            results.clear()

    # Insert remaining records.
    if attempts:
        db.add_all(attempts)
        db.flush()

        db.add_all(results)
        db.flush()

    db.commit()

    print("\nAttempt data generated successfully!")
    print(f"Attempts: {db.query(Attempt).count()}")
    print(
        "Assessment results: "
        f"{db.query(AssessmentResult).count()}"
    )


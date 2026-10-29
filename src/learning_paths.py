from sqlalchemy.orm import Session
from config.settings import ID_YEAR
from src.models import (
    Learner,
    Course,
    ContentItem,
    ContentSkill,
    Skill,
    SkillPrerequisite,
    Attempt,
    LearningPath,
)
from src.mastery import calculate_skill_mastery


def create_learning_path(
    db: Session,
    learner_id: str,
    course_id: str,
) -> LearningPath:
    """
    Create a learning path for an active learner and published course.

    If an active path already exists for this learner and course,
    return the existing path instead of creating a duplicate.
    """

    # 1. Validate the learner.
    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise ValueError(f"Learner not found: {learner_id}")

    if learner.status != "ACTIVE":
        raise ValueError(
            "Cannot create a learning path for an inactive learner."
        )

    # 2. Validate the course.
    course = (
        db.query(Course)
        .filter(Course.course_id == course_id)
        .first()
    )

    if course is None:
        raise ValueError(f"Course not found: {course_id}")

    if course.status != "PUBLISHED":
        raise ValueError(
            "Learning paths require a published course."
        )

    # 3. Reuse an existing active learning path.
    existing_path = (
        db.query(LearningPath)
        .filter(
            LearningPath.learner_id == learner_id,
            LearningPath.course_id == course_id,
            LearningPath.status == "ACTIVE",
        )
        .first()
    )

    if existing_path is not None:
        return existing_path

    # 4. Generate a unique learning path ID.
    # Check existing IDs rather than relying only on the row count.
    existing_ids = {
        row[0]
        for row in db.query(LearningPath.learning_path_id).all()
    }

    number = 1

    while True:
        learning_path_id = f"PATH-{ID_YEAR}-{number:06d}"

        if learning_path_id not in existing_ids:
            break

        number += 1

    # 5. Create the learning path.
    learning_path = LearningPath(
        learning_path_id=learning_path_id,
        learner_id=learner_id,
        course_id=course_id,
        status="ACTIVE",
        version=1,
    )

    try:
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)
    except Exception:
        db.rollback()
        raise

    return learning_path


def get_learning_path_content(
    db: Session,
    learner_id: str,
    course_id: str,
) -> list[dict]:
    """
    Return eligible course content ordered by difficulty and mastery.

    Rules:
    - Only active learners can receive content.
    - The course must be published.
    - Only published content is included.
    - Previously completed content is excluded.
    - Skills must be active.
    - Active prerequisites must have mastery of at least 70%.
    - Beginner content is ordered before intermediate and advanced content.
    """

    # 1. Validate the learner.
    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise ValueError(f"Learner not found: {learner_id}")

    if learner.status != "ACTIVE":
        return []

    # 2. Validate the course.
    course = (
        db.query(Course)
        .filter(Course.course_id == course_id)
        .first()
    )

    if course is None or course.status != "PUBLISHED":
        return []

    # 3. Calculate the learner's skill mastery.
    mastery = calculate_skill_mastery(db, learner_id)

    # 4. Find content the learner has already completed.
    completed_content_ids = {
        row[0]
        for row in (
            db.query(Attempt.content_id)
            .filter(
                Attempt.learner_id == learner_id,
                Attempt.status == "COMPLETED",
            )
            .distinct()
            .all()
        )
    }

    # 5. Retrieve published content belonging to the course.
    content_items = (
        db.query(ContentItem)
        .filter(
            ContentItem.course_id == course_id,
            ContentItem.status == "PUBLISHED",
        )
        .all()
    )

    difficulty_order = {
        "BEGINNER": 1,
        "INTERMEDIATE": 2,
        "ADVANCED": 3,
    }

    eligible_items = []

    # 6. Check each content item.
    for content in content_items:

        # Skip content already completed by the learner.
        if content.content_id in completed_content_ids:
            continue

        # Find the skills associated with this content.
        mappings = (
            db.query(ContentSkill)
            .filter(
                ContentSkill.content_id == content.content_id
            )
            .all()
        )

        # Skip content without skill mappings.
        if not mappings:
            continue

        eligible = True
        lowest_mastery = 100.0

        for mapping in mappings:

            # Check whether the mapped skill exists and is active.
            skill = (
                db.query(Skill)
                .filter(Skill.skill_id == mapping.skill_id)
                .first()
            )

            if skill is None or skill.status != "ACTIVE":
                eligible = False
                break

            # Get the learner's mastery score for this skill.
            current_mastery = mastery.get(
                skill.skill_id,
                {"mastery_score": 0.0},
            )["mastery_score"]

            lowest_mastery = min(
                lowest_mastery,
                current_mastery,
            )

            # Find active prerequisites for this skill.
            prerequisites = (
                db.query(SkillPrerequisite)
                .filter(
                    SkillPrerequisite.skill_id == skill.skill_id,
                    SkillPrerequisite.status == "ACTIVE",
                )
                .all()
            )

            # Require at least 70% mastery of every prerequisite.
            for prerequisite in prerequisites:
                prerequisite_mastery = mastery.get(
                    prerequisite.prerequisite_skill_id,
                    {"mastery_score": 0.0},
                )["mastery_score"]

                if prerequisite_mastery < 70:
                    eligible = False
                    break

            if not eligible:
                break

        # 7. Add content only if all checks pass.
        if eligible:
            eligible_items.append(
                {
                    "content_id": content.content_id,
                    "title": content.title,
                    "difficulty": content.difficulty,
                    "estimated_minutes": content.estimated_minutes,
                    "mastery_score": round(
                        lowest_mastery,
                        2,
                    ),
                }
            )

    # 8. Order content from beginner to advanced.
    eligible_items.sort(
        key=lambda item: (
            difficulty_order.get(item["difficulty"], 99),
            item["mastery_score"],
            item["content_id"],
        )
    )

    return eligible_items


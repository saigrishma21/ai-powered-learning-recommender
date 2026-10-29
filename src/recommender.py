from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from src.models import (
    Learner,
    Skill,
    SkillPrerequisite,
    ContentItem,
    ContentSkill,
    Attempt,
    Recommendation,
)

from src.mastery import calculate_skill_mastery


def get_current_time() -> datetime:
    """Return the current UTC time as a naive datetime."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_recommendations(
    db: Session,
    learner_id: str,
    limit: int = 10,
    as_of: datetime | None = None,
) -> list[dict]:
    """
    Generate personalized recommendations using skill mastery,
    prerequisite rules, content availability, and completion history.

    Args:
        db: Active SQLAlchemy database session.
        learner_id: ID of the learner.
        limit: Maximum number of recommendations to return.
        as_of: Optional evaluation timestamp. Future assessments
               and future prerequisite changes are excluded.

    Returns:
        A ranked list of recommendation dictionaries.
    """

    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise ValueError(f"Learner not found: {learner_id}")

    if learner.status != "ACTIVE" or limit <= 0:
        return []

    # Use one consistent timestamp throughout the evaluation.
    evaluation_time = as_of or get_current_time()

    # Calculate mastery using only assessments available
    # at or before the evaluation timestamp.
    mastery = calculate_skill_mastery(
        db,
        learner_id,
        as_of=evaluation_time,
    )

    # Exclude content completed by the evaluation timestamp.
    completed_content_ids = {
        row[0]
        for row in (
            db.query(Attempt.content_id)
            .filter(
                Attempt.learner_id == learner_id,
                Attempt.status == "COMPLETED",
                Attempt.completed_at.isnot(None),
                Attempt.completed_at <= evaluation_time,
            )
            .distinct()
            .all()
        )
    }

    # Only content published by the evaluation timestamp
    # should be eligible.
    content_items = (
        db.query(ContentItem)
        .filter(
            ContentItem.status == "PUBLISHED",
            ContentItem.created_at <= evaluation_time,
        )
        .order_by(ContentItem.content_id)
        .all()
    )

    recommendations = []

    for content in content_items:

        if content.content_id in completed_content_ids:
            continue

        mappings = (
            db.query(ContentSkill)
            .filter(
                ContentSkill.content_id == content.content_id
            )
            .order_by(ContentSkill.skill_id)
            .all()
        )

        if not mappings:
            continue

        score = 0.0
        reasons = []
        eligible = True

        for mapping in mappings:

            skill = (
                db.query(Skill)
                .filter(
                    Skill.skill_id == mapping.skill_id
                )
                .first()
            )

            if skill is None or skill.status != "ACTIVE":
                eligible = False
                break

            skill_mastery = mastery.get(
                skill.skill_id,
                {"mastery_score": 0.0},
            )["mastery_score"]

            # Find prerequisites effective at evaluation time.
            prerequisite_rows = (
                db.query(SkillPrerequisite)
                .filter(
                    SkillPrerequisite.skill_id == skill.skill_id,
                    SkillPrerequisite.status == "ACTIVE",
                    SkillPrerequisite.effective_from <= evaluation_time,
                )
                .all()
            )

            for prerequisite in prerequisite_rows:

                # Ignore prerequisites that had expired
                # by the evaluation timestamp.
                if (
                    prerequisite.effective_to is not None
                    and prerequisite.effective_to <= evaluation_time
                ):
                    continue

                prerequisite_mastery = mastery.get(
                    prerequisite.prerequisite_skill_id,
                    {"mastery_score": 0.0},
                )["mastery_score"]

                if prerequisite_mastery < 70:
                    eligible = False
                    reasons.append(
                        "PREREQUISITE_NOT_MASTERED"
                    )
                    break

            if not eligible:
                break

            # Prioritize skills with lower mastery.
            gap_score = 100.0 - skill_mastery

            difficulty_bonus = {
                "BEGINNER": 15,
                "INTERMEDIATE": 10,
                "ADVANCED": 5,
            }.get(content.difficulty, 0)

            score += (
                gap_score + difficulty_bonus
            ) * float(mapping.contribution_weight)

            if skill_mastery < 40:
                reasons.append("LOW_SKILL_MASTERY")

            elif skill_mastery < 70:
                reasons.append("SKILL_DEVELOPMENT")

        if not eligible:
            continue

        # Ensure every recommendation has an explanation.
        if not reasons:
            reasons.append("CONTINUE_SKILL_DEVELOPMENT")

        recommendations.append(
            {
                "content_id": content.content_id,
                "title": content.title,
                "difficulty": content.difficulty,
                "recommendation_score": round(score, 2),
                "reason_codes": sorted(set(reasons)),
            }
        )

    # Highest score first; use content ID for deterministic tie-breaking.
    recommendations.sort(
        key=lambda item: (
            -item["recommendation_score"],
            item["content_id"],
        )
    )

    return recommendations[:limit]


def save_recommendations(
    db: Session,
    learner_id: str,
    recommendations: list[dict],
) -> int:
    """
    Save recommendations as new historical records.

    Each record receives a unique ID and timestamp.
    Existing recommendation records are never overwritten.
    """

    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise ValueError(f"Learner not found: {learner_id}")

    if learner.status != "ACTIVE" or not recommendations:
        return 0

    # Use one timestamp for this saved recommendation batch.
    recommended_at = get_current_time()

    # Calculate mastery as it existed at recommendation time.
    mastery = calculate_skill_mastery(
        db,
        learner_id,
        as_of=recommended_at,
    )

    new_records = []

    for item in recommendations:

        content_id = item["content_id"]

        # Never save a recommendation for unavailable content.
        content = (
            db.query(ContentItem)
            .filter(
                ContentItem.content_id == content_id,
                ContentItem.status == "PUBLISHED",
                ContentItem.created_at <= recommended_at,
            )
            .first()
        )

        if content is None:
            continue

        mappings = (
            db.query(ContentSkill)
            .filter(
                ContentSkill.content_id == content_id
            )
            .all()
        )

        mastery_scores = [
            mastery[mapping.skill_id]["mastery_score"]
            for mapping in mappings
            if mapping.skill_id in mastery
        ]

        average_mastery = (
            sum(mastery_scores) / len(mastery_scores)
            if mastery_scores
            else 0.0
        )

        new_records.append(
            Recommendation(
                recommendation_id=(
                    f"REC-{uuid4().hex.upper()}"
                ),
                learner_id=learner_id,
                content_id=content_id,
                learning_path_id=None,
                recommended_at=recommended_at,
                mastery_at_recommendation=round(
                    average_mastery, 2
                ),
                decision="RECOMMEND",
                reason_codes=item.get(
                    "reason_codes",
                    ["CONTINUE_SKILL_DEVELOPMENT"],
                ),
                status="GENERATED",
            )
        )

    if new_records:
        try:
            db.add_all(new_records)
            db.commit()

        except Exception:
            db.rollback()
            raise

    return len(new_records)

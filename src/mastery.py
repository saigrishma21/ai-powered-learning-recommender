from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from src.models import (
    Learner,
    Skill,
    ContentSkill,
    Attempt,
    AssessmentResult,
)


# Mastery thresholds used by our recommendation system.
BEGINNER_THRESHOLD = 40
DEVELOPING_THRESHOLD = 70
PROFICIENT_THRESHOLD = 85


def get_mastery_level(mastery_score: float) -> str:
    """Convert a mastery percentage into a descriptive level."""

    if mastery_score < BEGINNER_THRESHOLD:
        return "BEGINNER"

    if mastery_score < DEVELOPING_THRESHOLD:
        return "DEVELOPING"

    if mastery_score < PROFICIENT_THRESHOLD:
        return "PROFICIENT"

    return "ADVANCED"


def calculate_skill_mastery(
    db: Session,
    learner_id: str,
    as_of: datetime | None = None,
) -> dict:
    """
    Calculate a learner's mastery score for each skill.

    Only assessment results recorded at or before `as_of`
    are considered when an evaluation timestamp is provided.

    More recent assessment observations receive greater weight.

    Args:
        db: Active SQLAlchemy database session.
        learner_id: ID of the learner.
        as_of: Optional cutoff timestamp for historical evaluation.

    Returns:
        A dictionary containing each skill's mastery score,
        mastery level, and number of assessment results.
    """

    # 1. Verify that the learner exists.
    learner = (
        db.query(Learner)
        .filter(Learner.learner_id == learner_id)
        .first()
    )

    if learner is None:
        raise ValueError(f"Learner not found: {learner_id}")

    # 2. Retrieve available skills.
    skills = (
        db.query(Skill)
        .order_by(Skill.skill_id.asc())
        .all()
    )

    # 3. Store assessment observations for each skill.
    skill_observations = defaultdict(list)

    # 4. Build the assessment query.
    query = (
        db.query(
            Attempt.content_id,
            AssessmentResult.percentage,
            AssessmentResult.assessed_at,
        )
        .join(
            AssessmentResult,
            Attempt.attempt_id == AssessmentResult.attempt_id,
        )
        .filter(
            Attempt.learner_id == learner_id
        )
    )

    # 5. Exclude future assessment results when a cutoff
    # timestamp is provided.
    if as_of is not None:
        query = query.filter(
            AssessmentResult.assessed_at <= as_of
        )

    # Process assessments chronologically.
    results = (
        query
        .order_by(
            AssessmentResult.assessed_at.asc(),
            Attempt.attempt_id.asc(),
        )
        .all()
    )

    # 6. Map assessment scores to the skills covered
    # by each content item.
    for result in results:
        content_mappings = (
            db.query(ContentSkill)
            .filter(
                ContentSkill.content_id == result.content_id
            )
            .order_by(ContentSkill.skill_id.asc())
            .all()
        )

        for mapping in content_mappings:
            skill_observations[mapping.skill_id].append(
                float(result.percentage)
            )

    # 7. Calculate mastery for every skill.
    mastery = {}

    for skill in skills:
        observations = skill_observations.get(
            skill.skill_id, []
        )

        if not observations:
            score = 0.0

        else:
            # Later observations receive greater weights.
            weights = list(
                range(1, len(observations) + 1)
            )

            weighted_score = sum(
                value * weight
                for value, weight in zip(
                    observations, weights
                )
            )

            total_weight = sum(weights)

            score = weighted_score / total_weight

        # Keep mastery between 0 and 100.
        score = round(
            max(0.0, min(100.0, score)),
            2,
        )

        mastery[skill.skill_id] = {
            "skill_name": skill.skill_name,
            "mastery_score": score,
            "mastery_level": get_mastery_level(score),
            "assessment_count": len(observations),
        }

    return mastery


from sqlalchemy import func

from src import models


def validate_data(db):
    """Validate database integrity and business rules."""

    errors = []

    # --------------------------------------------------
    # 1. Essential tables must contain data.
    # --------------------------------------------------

    for model, label in [
        (models.Learner, "learners"),
        (models.Course, "courses"),
        (models.Skill, "skills"),
        (models.ContentItem, "content items"),
    ]:
        if db.query(model).count() == 0:
            errors.append(f"No {label} found.")

    # --------------------------------------------------
    # 2. Content must reference an existing course.
    # --------------------------------------------------

    invalid_content = (
        db.query(models.ContentItem)
        .outerjoin(
            models.Course,
            models.ContentItem.course_id == models.Course.course_id,
        )
        .filter(models.Course.course_id.is_(None))
        .count()
    )

    if invalid_content:
        errors.append(
            f"{invalid_content} content items reference missing courses."
        )

    # --------------------------------------------------
    # 3. Content-skill mappings must reference valid records.
    # --------------------------------------------------

    invalid_content_skills = (
        db.query(models.ContentSkill)
        .outerjoin(
            models.ContentItem,
            models.ContentSkill.content_id == models.ContentItem.content_id,
        )
        .filter(models.ContentItem.content_id.is_(None))
        .count()
    )

    if invalid_content_skills:
        errors.append(
            f"{invalid_content_skills} content-skill mappings "
            "reference missing content items."
        )

    invalid_skill_mappings = (
        db.query(models.ContentSkill)
        .outerjoin(
            models.Skill,
            models.ContentSkill.skill_id == models.Skill.skill_id,
        )
        .filter(models.Skill.skill_id.is_(None))
        .count()
    )

    if invalid_skill_mappings:
        errors.append(
            f"{invalid_skill_mappings} content-skill mappings "
            "reference missing skills."
        )

    # --------------------------------------------------
    # 4. Attempt timestamp and lifecycle consistency.
    # --------------------------------------------------

    invalid_timestamps = (
        db.query(models.Attempt)
        .filter(
            models.Attempt.completed_at.isnot(None),
            models.Attempt.completed_at < models.Attempt.started_at,
        )
        .count()
    )

    if invalid_timestamps:
        errors.append(
            f"{invalid_timestamps} attempts have invalid timestamps."
        )

    completed_without_timestamp = (
        db.query(models.Attempt)
        .filter(
            models.Attempt.status == "COMPLETED",
            models.Attempt.completed_at.is_(None),
        )
        .count()
    )

    if completed_without_timestamp:
        errors.append(
            f"{completed_without_timestamp} completed attempts "
            "have no completion timestamp."
        )

    unfinished_with_timestamp = (
        db.query(models.Attempt)
        .filter(
            models.Attempt.status.in_(["IN_PROGRESS", "ABANDONED"]),
            models.Attempt.completed_at.isnot(None),
        )
        .count()
    )

    if unfinished_with_timestamp:
        errors.append(
            f"{unfinished_with_timestamp} unfinished or abandoned "
            "attempts have completion timestamps."
        )

    # --------------------------------------------------
    # 5. Every attempt must have an assessment result.
    # --------------------------------------------------

    attempts_without_results = (
        db.query(models.Attempt)
        .outerjoin(
            models.AssessmentResult,
            models.Attempt.attempt_id == models.AssessmentResult.attempt_id,
        )
        .filter(models.AssessmentResult.result_id.is_(None))
        .count()
    )

    if attempts_without_results:
        errors.append(
            f"{attempts_without_results} attempts have no assessment result."
        )

    # --------------------------------------------------
    # 6. Assessment results must reference existing attempts.
    # --------------------------------------------------

    invalid_results = (
        db.query(models.AssessmentResult)
        .outerjoin(
            models.Attempt,
            models.AssessmentResult.attempt_id == models.Attempt.attempt_id,
        )
        .filter(models.Attempt.attempt_id.is_(None))
        .count()
    )

    if invalid_results:
        errors.append(
            f"{invalid_results} assessment results reference missing attempts."
        )

    # --------------------------------------------------
    # 7. Assessment score ranges and arithmetic reconciliation.
    # --------------------------------------------------

    invalid_scores = (
        db.query(models.AssessmentResult)
        .filter(
            (models.AssessmentResult.score < 0)
            | (
                models.AssessmentResult.score
                > models.AssessmentResult.max_score
            )
            | (models.AssessmentResult.max_score <= 0)
            | (models.AssessmentResult.percentage < 0)
            | (models.AssessmentResult.percentage > 100)
        )
        .count()
    )

    if invalid_scores:
        errors.append(
            f"{invalid_scores} assessment results have invalid scores."
        )

    # The generator rounds percentage to two decimal places.
    # Allow a small floating-point tolerance.
    invalid_percentages = (
        db.query(models.AssessmentResult)
        .filter(
            func.abs(
                models.AssessmentResult.percentage
                - (
                    models.AssessmentResult.score
                    * 100.0
                    / models.AssessmentResult.max_score
                )
            ) > 0.011
        )
        .count()
    )

    if invalid_percentages:
        errors.append(
            f"{invalid_percentages} assessment percentages do not "
            "match score/max_score."
        )

    # --------------------------------------------------
    # 8. Attempts must reference existing learners and content.
    # --------------------------------------------------

    invalid_attempt_learners = (
        db.query(models.Attempt)
        .outerjoin(
            models.Learner,
            models.Attempt.learner_id == models.Learner.learner_id,
        )
        .filter(models.Learner.learner_id.is_(None))
        .count()
    )

    if invalid_attempt_learners:
        errors.append(
            f"{invalid_attempt_learners} attempts reference missing learners."
        )

    invalid_attempt_content = (
        db.query(models.Attempt)
        .outerjoin(
            models.ContentItem,
            models.Attempt.content_id == models.ContentItem.content_id,
        )
        .filter(models.ContentItem.content_id.is_(None))
        .count()
    )

    if invalid_attempt_content:
        errors.append(
            f"{invalid_attempt_content} attempts reference missing content."
        )

    # --------------------------------------------------
    # 9. Prerequisites must reference valid skills.
    # --------------------------------------------------

    invalid_prerequisites = (
        db.query(models.SkillPrerequisite)
        .outerjoin(
            models.Skill,
            models.SkillPrerequisite.skill_id == models.Skill.skill_id,
        )
        .filter(models.Skill.skill_id.is_(None))
        .count()
    )

    if invalid_prerequisites:
        errors.append(
            f"{invalid_prerequisites} prerequisites reference missing skills."
        )

    invalid_prerequisite_targets = (
        db.query(models.SkillPrerequisite)
        .outerjoin(
            models.Skill,
            models.SkillPrerequisite.prerequisite_skill_id
            == models.Skill.skill_id,
        )
        .filter(models.Skill.skill_id.is_(None))
        .count()
    )

    if invalid_prerequisite_targets:
        errors.append(
            f"{invalid_prerequisite_targets} prerequisite targets "
            "reference missing skills."
        )

    self_prerequisites = (
        db.query(models.SkillPrerequisite)
        .filter(
            models.SkillPrerequisite.skill_id
            == models.SkillPrerequisite.prerequisite_skill_id
        )
        .count()
    )

    if self_prerequisites:
        errors.append(
            f"{self_prerequisites} skills incorrectly depend on themselves."
        )

    # --------------------------------------------------
    # 10. Check active prerequisite cycles.
    # --------------------------------------------------

    active_edges = (
        db.query(
            models.SkillPrerequisite.skill_id,
            models.SkillPrerequisite.prerequisite_skill_id,
        )
        .filter(models.SkillPrerequisite.status == "ACTIVE")
        .all()
    )

    graph = {}

    for skill_id, prerequisite_skill_id in active_edges:
        graph.setdefault(skill_id, set()).add(prerequisite_skill_id)

    visited = set()
    visiting = set()
    cycle_found = False

    def has_cycle(skill_id):
        nonlocal cycle_found

        if skill_id in visiting:
            cycle_found = True
            return True

        if skill_id in visited:
            return False

        visiting.add(skill_id)

        for prerequisite_id in graph.get(skill_id, set()):
            if has_cycle(prerequisite_id):
                return True

        visiting.remove(skill_id)
        visited.add(skill_id)

        return False

    for skill_id in graph:
        if skill_id not in visited and has_cycle(skill_id):
            break

    if cycle_found:
        errors.append(
            "Active skill prerequisites contain a cycle."
        )

    # --------------------------------------------------
    # 11. Check duplicate attempt numbers for each learner/content pair.
    # --------------------------------------------------

    duplicate_attempts = (
        db.query(
            models.Attempt.learner_id,
            models.Attempt.content_id,
            models.Attempt.attempt_number,
            func.count().label("total"),
        )
        .group_by(
            models.Attempt.learner_id,
            models.Attempt.content_id,
            models.Attempt.attempt_number,
        )
        .having(func.count() > 1)
        .count()
    )

    if duplicate_attempts:
        errors.append(
            f"{duplicate_attempts} duplicate learner/content/attempt "
            "number combinations found."
        )

    # --------------------------------------------------
    # 12. Learning paths must reference existing learners/courses.
    # --------------------------------------------------

    invalid_path_learners = (
        db.query(models.LearningPath)
        .outerjoin(
            models.Learner,
            models.LearningPath.learner_id == models.Learner.learner_id,
        )
        .filter(models.Learner.learner_id.is_(None))
        .count()
    )

    if invalid_path_learners:
        errors.append(
            f"{invalid_path_learners} learning paths reference missing learners."
        )

    invalid_path_courses = (
        db.query(models.LearningPath)
        .outerjoin(
            models.Course,
            models.LearningPath.course_id == models.Course.course_id,
        )
        .filter(models.Course.course_id.is_(None))
        .count()
    )

    if invalid_path_courses:
        errors.append(
            f"{invalid_path_courses} learning paths reference missing courses."
        )

    # --------------------------------------------------
    # 13. Recommendations must reference valid records.
    # --------------------------------------------------

    invalid_recommendation_learners = (
        db.query(models.Recommendation)
        .outerjoin(
            models.Learner,
            models.Recommendation.learner_id == models.Learner.learner_id,
        )
        .filter(models.Learner.learner_id.is_(None))
        .count()
    )

    if invalid_recommendation_learners:
        errors.append(
            f"{invalid_recommendation_learners} recommendations "
            "reference missing learners."
        )

    invalid_recommendation_content = (
        db.query(models.Recommendation)
        .outerjoin(
            models.ContentItem,
            models.Recommendation.content_id == models.ContentItem.content_id,
        )
        .filter(models.ContentItem.content_id.is_(None))
        .count()
    )

    if invalid_recommendation_content:
        errors.append(
            f"{invalid_recommendation_content} recommendations "
            "reference missing content."
        )

    invalid_recommendation_paths = (
        db.query(models.Recommendation)
        .outerjoin(
            models.LearningPath,
            models.Recommendation.learning_path_id
            == models.LearningPath.learning_path_id,
        )
        .filter(
            models.Recommendation.learning_path_id.isnot(None),
            models.LearningPath.learning_path_id.is_(None),
        )
        .count()
    )

    if invalid_recommendation_paths:
        errors.append(
            f"{invalid_recommendation_paths} recommendations "
            "reference missing learning paths."
        )

    return errors


def print_validation_report(db):
    """Print a validation report and return its success status."""

    print("\nRunning data integrity checks...\n")

    errors = validate_data(db)

    if errors:
        print("VALIDATION FAILED")

        for number, error in enumerate(errors, start=1):
            print(f"FAIL {number}: {error}")

        return False

    print("PASS: Essential tables contain data.")
    print("PASS: Content items reference existing courses.")
    print("PASS: Content-skill mappings reference valid records.")
    print("PASS: Attempt timestamps and lifecycle states are valid.")
    print("PASS: Every attempt has an assessment result.")
    print("PASS: Assessment results reference existing attempts.")
    print("PASS: Assessment scores and percentages are consistent.")
    print("PASS: Attempts reference existing learners and content.")
    print("PASS: Prerequisites reference valid skills.")
    print("PASS: Active prerequisite graph contains no cycles.")
    print("PASS: No duplicate attempt-number combinations found.")
    print("PASS: Learning paths reference valid learners and courses.")
    print("PASS: Recommendations reference valid related records.")
    print("\nAll data integrity checks passed!")

    return True

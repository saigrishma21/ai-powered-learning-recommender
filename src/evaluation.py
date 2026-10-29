"""Ground-truth evaluation for the learning recommendation system."""

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base
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
from src.recommender import generate_recommendations


GROUND_TRUTH = [
    {
        "scenario_id": "GT-001",
        "description": "Beginner learner should receive foundational content",
        "expected": "foundational",
    },
    {
        "scenario_id": "GT-002",
        "description": "Learner who mastered Python fundamentals should progress to advanced content",
        "expected": "advanced",
    },
    {
        "scenario_id": "GT-003",
        "description": "Learner who has not mastered prerequisites should not receive dependent content",
        "expected": "prerequisite",
    },
    {
        "scenario_id": "GT-004",
        "description": "Inactive learner should not receive recommendations",
        "expected": "inactive",
    },
    {
        "scenario_id": "GT-005",
        "description": "Advanced learner should receive suitable advanced content",
        "expected": "advanced",
    },
    {
        "scenario_id": "GT-006",
        "description": "Learner with low assessment scores should receive remedial content",
        "expected": "remedial",
    },
    {
        "scenario_id": "GT-007",
        "description": "Learner with high assessment scores should receive next-level content",
        "expected": "advanced",
    },
    {
        "scenario_id": "GT-008",
        "description": "Archived content should never be recommended",
        "expected": "archived",
    },
]


def add_content(
    db,
    course_id,
    content_id,
    title,
    difficulty,
    skill_id,
    status="PUBLISHED",
):
    """Create content and associate it with a skill."""

    content = ContentItem(
        content_id=content_id,
        course_id=course_id,
        title=title,
        content_type="VIDEO",
        difficulty=difficulty,
        estimated_minutes=20,
        status=status,
    )

    db.add(content)
    db.flush()

    mapping = ContentSkill(
        content_id=content_id,
        skill_id=skill_id,
        contribution_weight=1.0,
    )

    db.add(mapping)
    db.flush()

    return content


def add_assessment_history(db, learner_id, content_id, score):
    """Create a completed attempt and its assessment result."""

    started_time = datetime(2026, 1, 1, 10, 0, 0)
    completed_time = started_time + timedelta(minutes=20)

    attempt = Attempt(
        attempt_id=f"ATT-{learner_id}-{content_id}",
        learner_id=learner_id,
        content_id=content_id,
        attempt_number=1,
        started_at=started_time,
        completed_at=completed_time,
        status="COMPLETED",
    )

    db.add(attempt)
    db.flush()

    result = AssessmentResult(
        result_id=f"RES-{learner_id}-{content_id}",
        attempt_id=attempt.attempt_id,
        score=score,
        max_score=100,
        percentage=score,
        passed=score >= 70,
        assessed_at=completed_time,
    )

    db.add(result)
    db.flush()


def run_scenario(scenario_id):
    """Create an isolated test database and evaluate one scenario."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        learner = Learner(
            learner_id=f"LRN-{scenario_id}",
            name="Evaluation Learner",
            email=f"{scenario_id.lower()}@example.com",
            status="INACTIVE" if scenario_id == "GT-004" else "ACTIVE",
        )

        course = Course(
            course_id=f"CRS-{scenario_id}",
            title="Python Learning Course",
            description="Evaluation course",
            status="PUBLISHED",
        )

        foundation = Skill(
            skill_id=f"SKL-F-{scenario_id}",
            skill_name=f"Python Fundamentals {scenario_id}",
            description="Python foundation concepts",
            status="ACTIVE",
        )

        advanced_skill = Skill(
            skill_id=f"SKL-A-{scenario_id}",
            skill_name=f"Advanced Python {scenario_id}",
            description="Advanced Python concepts",
            status="ACTIVE",
        )

        db.add_all(
            [
                learner,
                course,
                foundation,
                advanced_skill,
            ]
        )

        db.flush()

        # Create the prerequisite relationship.
        db.add(
            SkillPrerequisite(
                skill_id=advanced_skill.skill_id,
                prerequisite_skill_id=foundation.skill_id,
                effective_from=datetime(2026, 1, 1),
                effective_to=None,
                status="ACTIVE",
            )
        )

        db.flush()

        # Add foundational learning content.
        add_content(
            db,
            course.course_id,
            "CNT-TEST-001",
            "Python Fundamentals",
            "BEGINNER",
            foundation.skill_id,
        )

        # Add advanced learning content.
        add_content(
            db,
            course.course_id,
            "CNT-TEST-002",
            "Advanced Python",
            "ADVANCED",
            advanced_skill.skill_id,
        )

        # Scenario-specific content.
        if scenario_id == "GT-003":
            add_content(
                db,
                course.course_id,
                "CNT-TEST-003",
                "Python Advanced Exercises",
                "ADVANCED",
                advanced_skill.skill_id,
            )

        elif scenario_id == "GT-008":
            add_content(
                db,
                course.course_id,
                "CNT-TEST-008",
                "Archived Python Lesson",
                "BEGINNER",
                foundation.skill_id,
                status="ARCHIVED",
            )

        # Scenario-specific assessment history.
        if scenario_id in {"GT-002", "GT-007"}:
            add_assessment_history(
                db,
                learner.learner_id,
                "CNT-TEST-001",
                95,
            )

        elif scenario_id == "GT-005":
            # Establish foundation mastery first.
            add_assessment_history(
                db,
                learner.learner_id,
                "CNT-TEST-001",
                95,
            )

            # Add advanced practice content.
            add_content(
                db,
                course.course_id,
                "CNT-TEST-005",
                "Advanced Python Practice",
                "ADVANCED",
                advanced_skill.skill_id,
            )

            # Record a high score on advanced practice.
            add_assessment_history(
                db,
                learner.learner_id,
                "CNT-TEST-005",
                95,
            )

        elif scenario_id == "GT-006":
            # Add separate remedial content.
            add_content(
                db,
                course.course_id,
                "CNT-TEST-006",
                "Python Basics Remedial Lesson",
                "BEGINNER",
                foundation.skill_id,
            )

            # Record a low score on foundational content.
            add_assessment_history(
                db,
                learner.learner_id,
                "CNT-TEST-001",
                20,
            )

        db.commit()

        # Generate recommendations.
        recommendations = generate_recommendations(
            db,
            learner.learner_id,
            limit=10,
        )

        # Extract recommended content IDs.
        content_ids = [
            item.get("content_id")
            if isinstance(item, dict)
            else getattr(item, "content_id", None)
            for item in recommendations
        ]

        # Evaluate expected behavior for each scenario.
        if scenario_id == "GT-001":
            passed = "CNT-TEST-001" in content_ids

        elif scenario_id in {"GT-002", "GT-007"}:
            passed = any(
                content_id in {"CNT-TEST-002", "CNT-TEST-003"}
                for content_id in content_ids
            )

        elif scenario_id == "GT-003":
            passed = "CNT-TEST-003" not in content_ids

        elif scenario_id == "GT-004":
            passed = len(recommendations) == 0

        elif scenario_id == "GT-005":
            passed = any(
                content_id in {"CNT-TEST-002", "CNT-TEST-005"}
                for content_id in content_ids
            )

        elif scenario_id == "GT-006":
            passed = any(
                content_id in {"CNT-TEST-001", "CNT-TEST-006"}
                for content_id in content_ids
            )

        elif scenario_id == "GT-008":
            passed = "CNT-TEST-008" not in content_ids

        else:
            passed = False

        description = next(
            scenario["description"]
            for scenario in GROUND_TRUTH
            if scenario["scenario_id"] == scenario_id
        )

        return {
            "scenario_id": scenario_id,
            "description": description,
            "passed": passed,
            "evaluated": True,
            "content_ids": content_ids,
            "recommendation_count": len(recommendations),
        }

    finally:
        db.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


def evaluate_recommendations(db=None):
    """Run all ground-truth scenarios and summarize the results."""

    results = [
        run_scenario(scenario["scenario_id"])
        for scenario in GROUND_TRUTH
    ]

    evaluated = [
        result
        for result in results
        if result["evaluated"]
    ]

    passed = sum(
        1 for result in evaluated if result["passed"]
    )

    failed = len(evaluated) - passed
    total = len(GROUND_TRUTH)
    not_evaluated = total - len(evaluated)

    pass_rate = (
        round((passed / len(evaluated)) * 100, 1)
        if evaluated
        else 0.0
    )

    return {
        "total_scenarios": total,
        "evaluated": len(evaluated),
        "passed": passed,
        "failed": failed,
        "not_evaluated": not_evaluated,
        "pass_rate": pass_rate,
        "results": results,
    }


def print_evaluation_report(report):
    """Print the evaluation report."""

    print("=" * 65)
    print("RECOMMENDATION EVALUATION REPORT")
    print("=" * 65)

    print(f"Total scenarios: {report['total_scenarios']}")
    print(f"Evaluated:       {report['evaluated']}")
    print(f"Passed:          {report['passed']}")
    print(f"Failed:          {report['failed']}")
    print(f"Not evaluated:   {report['not_evaluated']}")
    print(f"Pass rate:       {report['pass_rate']}%")

    print("-" * 65)

    for result in report["results"]:
        if not result["evaluated"]:
            status = "NOT EVALUATED"
        elif result["passed"]:
            status = "PASS"
        else:
            status = "FAIL"

        print(
            f"{result['scenario_id']} | {status} | "
            f"{result['description']}"
        )

        print(
            f"  Details: Recommendations returned: "
            f"{result['recommendation_count']}; "
            f"content IDs: {result['content_ids']}"
        )

    print("=" * 65)
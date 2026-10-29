from pathlib import Path

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src import models

DATABASE_URL = "sqlite:///./learning_dev.db"

PROJECT_ROOT = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_ROOT / "learning_dev.db"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


def main():
    if not DATABASE_PATH.exists():
        print("Development database not found!")
        print(f"Expected location: {DATABASE_PATH}")
        return

    db = SessionLocal()

    try:
        print("\n=== DEVELOPMENT DATABASE VERIFICATION ===")

        tables = [
            ("Learners", models.Learner),
            ("Courses", models.Course),
            ("Skills", models.Skill),
            ("Skill prerequisites", models.SkillPrerequisite),
            ("Content items", models.ContentItem),
            ("Content-skill mappings", models.ContentSkill),
            ("Attempts", models.Attempt),
            ("Assessment results", models.AssessmentResult),
            ("Learning paths", models.LearningPath),
            ("Recommendations", models.Recommendation),
        ]

        for label, model in tables:
            count = db.query(func.count()).select_from(model).scalar()
            print(f"{label}: {count}")

        # Verify that every assessment result references an attempt.
        orphan_results = (
            db.query(models.AssessmentResult)
            .outerjoin(
                models.Attempt,
                models.AssessmentResult.attempt_id
                == models.Attempt.attempt_id,
            )
            .filter(models.Attempt.attempt_id.is_(None))
            .count()
        )

        print(f"Orphan assessment results: {orphan_results}")

        # Verify that every attempt has an assessment result.
        attempts_without_results = (
            db.query(models.Attempt)
            .outerjoin(
                models.AssessmentResult,
                models.Attempt.attempt_id
                == models.AssessmentResult.attempt_id,
            )
            .filter(models.AssessmentResult.result_id.is_(None))
            .count()
        )

        print(
            "Attempts without assessment results: "
            f"{attempts_without_results}"
        )

        print("\nVerification completed.")

    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()


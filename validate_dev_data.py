import sys
from pathlib import Path

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src import models
from src.database import Base
from src.validator import print_validation_report


# Connect to the development database
DATABASE_URL = "sqlite:///./learning_dev.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Enable foreign key enforcement in SQLite
from sqlalchemy import event


@event.listens_for(engine, "connect")
def enable_foreign_keys(connection, record):
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def main():
    print("=" * 60)
    print("DEVELOPMENT DATABASE VALIDATION")
    print("=" * 60)

    # Check that the database file and tables exist
    if not Path("learning_dev.db").exists():
        print("FAIL: learning_dev.db was not found.")
        sys.exit(1)

    try:
        # Open a database session
        db = SessionLocal()

        # Check expected record counts
        expected_counts = {
            "Learners": (models.Learner, 100),
            "Courses": (models.Course, 10),
            "Skills": (models.Skill, 50),
            "Skill prerequisites": (models.SkillPrerequisite, 49),
            "Content items": (models.ContentItem, 100),
            "Content-skill mappings": (models.ContentSkill, 100),
            "Attempts": (models.Attempt, 5000),
            "Assessment results": (models.AssessmentResult, 5000),
        }

        counts_passed = True

        print("\n1. RECORD COUNT CHECKS")

        for name, (model, expected) in expected_counts.items():
            actual = db.query(func.count()).select_from(model).scalar()

            if actual == expected:
                print(f"PASS: {name}: {actual} records")
            else:
                print(
                    f"FAIL: {name}: expected {expected}, found {actual}"
                )
                counts_passed = False

        # Run the detailed validation checks
        print("\n2. DATA RELATIONSHIP AND INTEGRITY CHECKS")

        validation_passed = print_validation_report(db)

        # Print final result
        print("\n" + "=" * 60)

        if counts_passed and validation_passed:
            print("OVERALL RESULT: PASS")
            print("The development database passed all validation checks.")
        else:
            print("OVERALL RESULT: FAIL")
            print("Review the failed checks before proceeding.")

        print("=" * 60)

        # Exit with a failure code if any check failed
        if not counts_passed or not validation_passed:
            sys.exit(1)

    except Exception as error:
        print(f"\nVALIDATION ERROR: {error}")
        sys.exit(1)

    finally:
        if "db" in locals():
            db.close()
        engine.dispose()


if __name__ == "__main__":
    main()


import sys
from pathlib import Path

from sqlalchemy import create_engine, event, func
from sqlalchemy.orm import sessionmaker

# Make the project root available for imports.
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import settings
from src import models
from src.database import Base
from src import data_generator


# --------------------------------------------------
# 1. Configure full dataset sizes
# --------------------------------------------------

settings.NUM_LEARNERS = settings.FULL_NUM_LEARNERS
settings.NUM_COURSES = settings.FULL_NUM_COURSES
settings.NUM_SKILLS = settings.FULL_NUM_SKILLS
settings.NUM_CONTENT_ITEMS = settings.FULL_NUM_CONTENT_ITEMS
settings.NUM_ATTEMPTS = settings.FULL_NUM_ATTEMPTS


# Update the constants imported directly by data_generator.py.
data_generator.NUM_LEARNERS = settings.FULL_NUM_LEARNERS
data_generator.NUM_COURSES = settings.FULL_NUM_COURSES
data_generator.NUM_SKILLS = settings.FULL_NUM_SKILLS
data_generator.NUM_CONTENT_ITEMS = settings.FULL_NUM_CONTENT_ITEMS
data_generator.NUM_ATTEMPTS = settings.FULL_NUM_ATTEMPTS


# --------------------------------------------------
# 2. Use a separate full dataset database
# --------------------------------------------------

DATABASE_URL = "sqlite:///./learning_full.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


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


def get_count(db, model):
    return db.query(func.count()).select_from(model).scalar()


def main():
    print("=" * 60)
    print("YOTTAFLEX AI - FULL DATASET GENERATION")
    print("=" * 60)

    # Create tables if they do not already exist.
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Do not accidentally add duplicate data to an existing database.
        existing_learners = get_count(db, models.Learner)

        if existing_learners > 0:
            raise RuntimeError(
                "learning_full.db already contains learners. "
                "Generation stopped to prevent duplicate data. "
                "Inspect the database before deciding how to proceed."
            )

        print("\nGenerating master data...")

        data_generator.generate_master_data(db)

        print("\nGenerating attempts and assessment results...")

        data_generator.generate_attempts(db)

        print("\nChecking generated record counts...")

        expected_counts = {
            "Learners": (
                models.Learner,
                settings.FULL_NUM_LEARNERS,
            ),
            "Courses": (
                models.Course,
                settings.FULL_NUM_COURSES,
            ),
            "Skills": (
                models.Skill,
                settings.FULL_NUM_SKILLS,
            ),
            "Content items": (
                models.ContentItem,
                settings.FULL_NUM_CONTENT_ITEMS,
            ),
            "Attempts": (
                models.Attempt,
                settings.FULL_NUM_ATTEMPTS,
            ),
            "Assessment results": (
                models.AssessmentResult,
                settings.FULL_NUM_ATTEMPTS,
            ),
        }

        all_counts_correct = True

        for name, (model, expected) in expected_counts.items():
            actual = get_count(db, model)

            if actual == expected:
                print(f"PASS: {name}: {actual:,}")
            else:
                print(
                    f"FAIL: {name}: expected {expected:,}, "
                    f"found {actual:,}"
                )
                all_counts_correct = False

        if not all_counts_correct:
            raise RuntimeError(
                "Some generated record counts do not match expectations."
            )

        print("\nFULL DATASET GENERATION COMPLETED SUCCESSFULLY.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()


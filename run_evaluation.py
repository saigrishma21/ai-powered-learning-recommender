from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.evaluation import (
    evaluate_recommendations,
    print_evaluation_report,
)

# Connect to the development database.
DATABASE_URL = "sqlite:///./learning_dev.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def main():
    db = SessionLocal()

    try:
        report = evaluate_recommendations(db)
        print_evaluation_report(report)
    finally:
        db.close()


if __name__ == "__main__":
    main()


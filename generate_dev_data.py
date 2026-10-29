import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src import models

from src.data_generator import (
    generate_master_data,
    generate_attempts,
)


DATABASE_URL = "sqlite:///./learning_dev.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


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
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        generate_master_data(db)
        generate_attempts(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
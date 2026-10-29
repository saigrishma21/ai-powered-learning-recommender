import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import Base, SessionLocal, engine
from src import models
from src.data_generator import (
    generate_master_data,
    generate_attempts,
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
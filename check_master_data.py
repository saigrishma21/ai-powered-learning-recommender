from src.database import SessionLocal
from src.models import (
    Learner,
    Course,
    Skill,
    SkillPrerequisite,
    ContentItem,
    ContentSkill,
)

db = SessionLocal()

try:
    print("MASTER DATA VALIDATION")
    print("-" * 35)

    tables = [
        ("Learners", Learner),
        ("Courses", Course),
        ("Skills", Skill),
        ("Prerequisites", SkillPrerequisite),
        ("Content items", ContentItem),
        ("Content-skill mappings", ContentSkill),
    ]

    for name, model in tables:
        print(f"{name}: {db.query(model).count()}")

    print("\nSample learner IDs:")

    learners = (
        db.query(Learner)
        .order_by(Learner.learner_id)
        .limit(3)
        .all()
    )

    for learner in learners:
        print(learner.learner_id, learner.name)

    print("\nSample content IDs:")

    content_items = (
        db.query(ContentItem)
        .order_by(ContentItem.content_id)
        .limit(3)
        .all()
    )

    for content in content_items:
        print(content.content_id, content.title)

finally:
    db.close()
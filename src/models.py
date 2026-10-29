from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    JSON,
)

from src.database import Base


class Learner(Base):
    __tablename__ = "learners"

    learner_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')",
            name="ck_learner_status",
        ),
    )


class Course(Base):
    __tablename__ = "courses"

    course_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="DRAFT")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')",
            name="ck_course_status",
        ),
    )


class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(String, primary_key=True)
    skill_name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_skill_status",
        ),
    )


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    prerequisite_id = Column(Integer, primary_key=True, autoincrement=True)

    skill_id = Column(
        String,
        ForeignKey("skills.skill_id"),
        nullable=False,
    )

    prerequisite_skill_id = Column(
        String,
        ForeignKey("skills.skill_id"),
        nullable=False,
    )

    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="ACTIVE")

    __table_args__ = (
        CheckConstraint(
            "skill_id != prerequisite_skill_id",
            name="ck_no_self_prerequisite",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to > effective_from",
            name="ck_prerequisite_dates",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_prerequisite_status",
        ),
        UniqueConstraint(
            "skill_id",
            "prerequisite_skill_id",
            "effective_from",
            name="uq_skill_prerequisite_period",
        ),
    )


class ContentItem(Base):
    __tablename__ = "content_items"

    content_id = Column(String, primary_key=True)

    course_id = Column(
        String,
        ForeignKey("courses.course_id"),
        nullable=False,
    )

    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    estimated_minutes = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="DRAFT")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "content_type IN "
            "('VIDEO', 'ARTICLE', 'QUIZ', 'EXERCISE', 'PROJECT')",
            name="ck_content_type",
        ),
        CheckConstraint(
            "difficulty IN ('BEGINNER', 'INTERMEDIATE', 'ADVANCED')",
            name="ck_content_difficulty",
        ),
        CheckConstraint(
            "estimated_minutes > 0",
            name="ck_content_duration",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')",
            name="ck_content_status",
        ),
    )


class ContentSkill(Base):
    __tablename__ = "content_skills"

    content_skill_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    content_id = Column(
        String,
        ForeignKey("content_items.content_id"),
        nullable=False,
    )

    skill_id = Column(
        String,
        ForeignKey("skills.skill_id"),
        nullable=False,
    )

    contribution_weight = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "content_id",
            "skill_id",
            name="uq_content_skill",
        ),
        CheckConstraint(
            "contribution_weight > 0 AND contribution_weight <= 1",
            name="ck_contribution_weight",
        ),
    )


class Attempt(Base):
    __tablename__ = "attempts"

    attempt_id = Column(String, primary_key=True)

    learner_id = Column(
        String,
        ForeignKey("learners.learner_id"),
        nullable=False,
    )

    content_id = Column(
        String,
        ForeignKey("content_items.content_id"),
        nullable=False,
    )

    attempt_number = Column(Integer, nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="IN_PROGRESS")

    __table_args__ = (
        UniqueConstraint(
            "learner_id",
            "content_id",
            "attempt_number",
            name="uq_learner_content_attempt",
        ),
        CheckConstraint(
            "attempt_number > 0",
            name="ck_attempt_number",
        ),
        CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="ck_attempt_dates",
        ),
        CheckConstraint(
            "status IN ('IN_PROGRESS', 'COMPLETED', 'ABANDONED')",
            name="ck_attempt_status",
        ),
    )


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    result_id = Column(String, primary_key=True)

    attempt_id = Column(
        String,
        ForeignKey("attempts.attempt_id"),
        nullable=False,
        unique=True,
    )

    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    assessed_at = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "score >= 0 AND score <= max_score",
            name="ck_assessment_score",
        ),
        CheckConstraint(
            "max_score > 0",
            name="ck_assessment_max_score",
        ),
        CheckConstraint(
            "percentage >= 0 AND percentage <= 100",
            name="ck_assessment_percentage",
        ),
    )


class LearningPath(Base):
    __tablename__ = "learning_paths"

    learning_path_id = Column(String, primary_key=True)

    learner_id = Column(
        String,
        ForeignKey("learners.learner_id"),
        nullable=False,
    )

    course_id = Column(
        String,
        ForeignKey("courses.course_id"),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    version = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'COMPLETED', 'PAUSED', 'CANCELLED')",
            name="ck_learning_path_status",
        ),
        CheckConstraint(
            "version > 0",
            name="ck_learning_path_version",
        ),
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String, primary_key=True)

    learner_id = Column(
        String,
        ForeignKey("learners.learner_id"),
        nullable=False,
    )

    content_id = Column(
        String,
        ForeignKey("content_items.content_id"),
        nullable=False,
    )

    learning_path_id = Column(
        String,
        ForeignKey("learning_paths.learning_path_id"),
        nullable=True,
    )

    recommended_at = Column(DateTime, nullable=False)
    mastery_at_recommendation = Column(Float, nullable=False)
    decision = Column(String, nullable=False)
    reason_codes = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="GENERATED")

    __table_args__ = (
        CheckConstraint(
            "mastery_at_recommendation >= 0 "
            "AND mastery_at_recommendation <= 100",
            name="ck_recommendation_mastery",
        ),
        CheckConstraint(
            "decision IN ('RECOMMEND', 'REJECT')",
            name="ck_recommendation_decision",
        ),
        CheckConstraint(
            "status IN "
            "('GENERATED', 'ACCEPTED', 'STARTED', "
            "'COMPLETED', 'DISMISSED')",
            name="ck_recommendation_status",
        ),
    )

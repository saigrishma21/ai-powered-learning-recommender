# AI-Powered Personalized Learning Recommendation System

## Data Dictionary and Schema Reference

### 1. Purpose

This document describes the data entities, fields, relationships, validation rules, and lifecycle states used by the AI-Powered Personalized Learning Recommendation System.

The system recommends learning activities based on learner skills, prerequisite relationships, assessment results, and content difficulty.

**Important:** This document specifies the intended data contract. Database constraints and application-level validations must be checked against the actual implementation.

---

# 2. Learner

**Purpose:** Stores learner information.

**Primary key:** `learner_id`

| Field      | Data type   | Required | Unique | Allowed values / validation                        |
| ---------- | ----------- | -------- | ------ | -------------------------------------------------- |
| learner_id | String      | Yes      | Yes    | Immutable identifier; expected format `LRN-000001` |
| name       | String      | Yes      | No     | Must not be null                                   |
| email      | String      | Yes      | Yes    | Must be unique                                     |
| created_at | DateTime    | Yes      | No     | Learner creation timestamp                         |
| status     | Enum/String | Yes      | No     | `ACTIVE`, `INACTIVE`, `SUSPENDED`                  |

**Relationships**

* One learner can have many attempts.
* One learner can have many learning paths.
* One learner can have many recommendation records.

**Lifecycle:** `ACTIVE`, `INACTIVE`, `SUSPENDED`.

---

# 3. Course

**Purpose:** Stores course information.

**Primary key:** `course_id`

| Field       | Data type   | Required | Unique | Allowed values / validation      |
| ----------- | ----------- | -------- | ------ | -------------------------------- |
| course_id   | String      | Yes      | Yes    | Expected format `CRS-000001`     |
| title       | String      | Yes      | No     | Must not be null                 |
| description | String      | No       | No     | Optional descriptive text        |
| status      | Enum/String | Yes      | No     | `DRAFT`, `PUBLISHED`, `ARCHIVED` |
| created_at  | DateTime    | Yes      | No     | Course creation timestamp        |

**Relationships**

* One course can contain many content items.
* One course can be associated with many learning paths.

**Lifecycle:** `DRAFT`, `PUBLISHED`, `ARCHIVED`.

---

# 4. Skill

**Purpose:** Stores individual skills that learners can develop.

**Primary key:** `skill_id`

| Field       | Data type   | Required | Unique | Allowed values / validation  |
| ----------- | ----------- | -------- | ------ | ---------------------------- |
| skill_id    | String      | Yes      | Yes    | Expected format `SKL-000001` |
| skill_name  | String      | Yes      | Yes    | Must be unique               |
| description | String      | No       | No     | Optional descriptive text    |
| status      | Enum/String | Yes      | No     | `ACTIVE`, `INACTIVE`         |
| created_at  | DateTime    | Yes      | No     | Skill creation timestamp     |

**Relationships**

* A skill can have many prerequisite relationships.
* A skill can map to many content items through `ContentSkill`.
* A skill can be a prerequisite for other skills.

**Lifecycle:** `ACTIVE`, `INACTIVE`.

---

# 5. SkillPrerequisite

**Purpose:** Defines which skills must be mastered before another skill is considered eligible for progression.

**Primary key:** `prerequisite_id`

| Field                 | Data type   | Required | Unique | Allowed values / validation                                 |
| --------------------- | ----------- | -------- | ------ | ----------------------------------------------------------- |
| prerequisite_id       | Integer     | Yes      | Yes    | Database-generated primary key                              |
| skill_id              | String      | Yes      | No     | Foreign key referencing `Skill.skill_id`                    |
| prerequisite_skill_id | String      | Yes      | No     | Foreign key referencing `Skill.skill_id`                    |
| effective_from        | DateTime    | Yes      | No     | Start of the relationship's validity                        |
| effective_to          | DateTime    | No       | No     | Optional end of validity; must not precede `effective_from` |
| status                | Enum/String | Yes      | No     | `ACTIVE`, `INACTIVE`                                        |

**Validation rules**

* A skill cannot be its own prerequisite.
* Both skill references must exist.
* Duplicate prerequisite relationships for the same effective period must be prevented.
* Prerequisite cycles must be detected.
* An inactive or expired relationship must not be treated as an active prerequisite.

**Relationships**

Each prerequisite record references two skill records. A skill may have multiple prerequisites and may be a prerequisite for multiple other skills.

**Cardinality:** Skill-to-skill is a recursive many-to-many relationship implemented through this entity.

---

# 6. ContentItem

**Purpose:** Stores videos, articles, quizzes, exercises, and projects available to learners.

**Primary key:** `content_id`

| Field             | Data type   | Required | Unique | Allowed values / validation                       |
| ----------------- | ----------- | -------- | ------ | ------------------------------------------------- |
| content_id        | String      | Yes      | Yes    | Expected format `CNT-000001`                      |
| course_id         | String      | Yes      | No     | Foreign key referencing `Course.course_id`        |
| title             | String      | Yes      | No     | Must not be null                                  |
| content_type      | Enum/String | Yes      | No     | `VIDEO`, `ARTICLE`, `QUIZ`, `EXERCISE`, `PROJECT` |
| difficulty        | Enum/String | Yes      | No     | `BEGINNER`, `INTERMEDIATE`, `ADVANCED`            |
| estimated_minutes | Integer     | Yes      | No     | Must be greater than zero; unit is minutes        |
| status            | Enum/String | Yes      | No     | `DRAFT`, `PUBLISHED`, `ARCHIVED`                  |
| created_at        | DateTime    | Yes      | No     | Content creation timestamp                        |

**Relationships**

* Many content items can belong to one course.
* A content item can map to many skills through `ContentSkill`.
* A content item can have many learner attempts.
* A content item can appear in many recommendation records.

**Lifecycle:** `DRAFT`, `PUBLISHED`, `ARCHIVED`.

Only eligible published content should be recommended.

---

# 7. ContentSkill

**Purpose:** Maps content items to the skills they teach or assess.

**Primary key:** `content_skill_id`

| Field               | Data type     | Required | Unique | Allowed values / validation                      |
| ------------------- | ------------- | -------- | ------ | ------------------------------------------------ |
| content_skill_id    | Integer       | Yes      | Yes    | Database-generated primary key                   |
| content_id          | String        | Yes      | No     | Foreign key referencing `ContentItem.content_id` |
| skill_id            | String        | Yes      | No     | Foreign key referencing `Skill.skill_id`         |
| contribution_weight | Float/Decimal | Yes      | No     | Must be greater than 0 and at most 1             |

**Validation rules**

* Both referenced records must exist.
* The combination of `content_id` and `skill_id` must be unique.
* Contribution weights must satisfy `0 < contribution_weight <= 1`.

**Relationships**

This is a bridge entity implementing a many-to-many relationship between content items and skills.

A content item may contribute to multiple skills, and a skill may be taught or assessed by multiple content items.

---

# 8. Attempt

**Purpose:** Records a learner's interaction with a content item over time.

**Primary key:** `attempt_id`

| Field          | Data type   | Required | Unique | Allowed values / validation                      |
| -------------- | ----------- | -------- | ------ | ------------------------------------------------ |
| attempt_id     | String      | Yes      | Yes    | Expected pattern `ATT-<learner-id>-000001`       |
| learner_id     | String      | Yes      | No     | Foreign key referencing `Learner.learner_id`     |
| content_id     | String      | Yes      | No     | Foreign key referencing `ContentItem.content_id` |
| attempt_number | Integer     | Yes      | No     | Must be greater than zero                        |
| started_at     | DateTime    | Yes      | No     | Attempt start timestamp                          |
| completed_at   | DateTime    | No       | No     | If present, must not precede `started_at`        |
| status         | Enum/String | Yes      | No     | `IN_PROGRESS`, `COMPLETED`, `ABANDONED`          |

**Validation rules**

* Learner and content references must exist.
* Attempt identifiers must be immutable.
* Attempt numbers must be positive.
* The combination of learner, content, and attempt number must be unique.
* A completion timestamp cannot precede the start timestamp.
* Completed attempts should have consistent completion information.
* Repeated attempts must be represented as separate records.

**Relationships**

* One learner can have many attempts.
* One content item can have many attempts.
* One attempt can have at most one assessment result.

**Lifecycle:** `IN_PROGRESS`, `COMPLETED`, `ABANDONED`.

---

# 9. AssessmentResult

**Purpose:** Stores the assessment score associated with an attempt.

**Primary key:** `result_id`

| Field       | Data type | Required | Unique | Allowed values / validation                   |
| ----------- | --------- | -------- | ------ | --------------------------------------------- |
| result_id   | String    | Yes      | Yes    | Immutable result identifier                   |
| attempt_id  | String    | Yes      | Yes    | Foreign key referencing `Attempt.attempt_id`  |
| score       | Numeric   | Yes      | No     | Must be greater than or equal to zero         |
| max_score   | Numeric   | Yes      | No     | Must be greater than zero                     |
| percentage  | Numeric   | Yes      | No     | Must be between 0 and 100                     |
| passed      | Boolean   | Yes      | No     | Derived from the documented passing threshold |
| assessed_at | DateTime  | Yes      | No     | Assessment timestamp                          |

**Validation rules**

* The attempt reference must exist.
* Each attempt may have at most one assessment result under the current model.
* `0 <= score <= max_score`.
* `percentage` must be calculated from the source scores.

Expected calculation:

`percentage = (score / max_score) * 100`

The stored percentage should reconcile with this calculation within an explicitly documented rounding tolerance.

The passing threshold must be consistently configured. The current project configuration specifies 70%.

**Relationship cardinality:** Attempt-to-AssessmentResult is one-to-zero-or-one.

---

# 10. LearningPath

**Purpose:** Represents a learner's learning path through a course.

**Primary key:** `learning_path_id`

| Field            | Data type   | Required | Unique | Allowed values / validation                  |
| ---------------- | ----------- | -------- | ------ | -------------------------------------------- |
| learning_path_id | String      | Yes      | Yes    | Required convention: `PATH-2026-000001`      |
| learner_id       | String      | Yes      | No     | Foreign key referencing `Learner.learner_id` |
| course_id        | String      | Yes      | No     | Foreign key referencing `Course.course_id`   |
| created_at       | DateTime    | Yes      | No     | Path creation timestamp                      |
| status           | Enum/String | Yes      | No     | `ACTIVE`, `COMPLETED`, `PAUSED`, `CANCELLED` |
| version          | Integer     | Yes      | No     | Must be greater than zero                    |

**Validation rules**

* Learner and course references must exist.
* Version must be positive.
* Lifecycle transitions must be validated.
* Repeated paths without progress must be detected.
* A path must not repeatedly recommend the same activity without a documented reason or progress.

**Relationships**

* One learner may have many learning paths.
* One course may be associated with many learning paths.
* A recommendation may optionally reference a learning path.

**Lifecycle:** `ACTIVE`, `COMPLETED`, `PAUSED`, `CANCELLED`.

---

# 11. Recommendation

**Purpose:** Records recommended learning activities, their rationale, and subsequent outcomes.

**Primary key:** `recommendation_id`

| Field                     | Data type   | Required | Unique | Allowed values / validation                                      |
| ------------------------- | ----------- | -------- | ------ | ---------------------------------------------------------------- |
| recommendation_id         | String      | Yes      | Yes    | Immutable recommendation identifier                              |
| learner_id                | String      | Yes      | No     | Foreign key referencing `Learner.learner_id`                     |
| content_id                | String      | Yes      | No     | Foreign key referencing `ContentItem.content_id`                 |
| learning_path_id          | String      | No       | No     | Optional foreign key referencing `LearningPath.learning_path_id` |
| recommended_at            | DateTime    | Yes      | No     | Recommendation generation timestamp                              |
| mastery_at_recommendation | Numeric     | Yes      | No     | Must be between 0 and 100                                        |
| decision                  | Enum/String | Yes      | No     | `RECOMMEND`, `REJECT`                                            |
| reason_codes              | JSON        | Yes      | No     | Must contain meaningful rationale codes                          |
| status                    | Enum/String | Yes      | No     | `GENERATED`, `ACCEPTED`, `STARTED`, `COMPLETED`, `DISMISSED`     |

**Validation rules**

* Learner and content references must exist.
* A learning path reference is optional, but must be valid when provided.
* Mastery values must be between 0 and 100.
* Reason codes must explain the recommendation decision.
* Prerequisite eligibility must be evaluated using the appropriate skill mastery.
* Mastery calculations must use only information available at the evaluation timestamp.
* Recommendation history must be preserved rather than silently overwritten.

**Relationships**

* One learner can have many recommendations.
* One content item can appear in many recommendation records.
* One learning path can be associated with many recommendations.
* A recommendation may exist without a learning path.

**Lifecycle:** `GENERATED`, `ACCEPTED`, `STARTED`, `COMPLETED`, `DISMISSED`.

---

# 12. Relationship and Cardinality Summary

| Relationship                   | Cardinality   | Implementation                       |
| ------------------------------ | ------------- | ------------------------------------ |
| Learner to Attempt             | 1:N           | `Attempt.learner_id`                 |
| ContentItem to Attempt         | 1:N           | `Attempt.content_id`                 |
| Attempt to AssessmentResult    | 1:0..1        | Unique `AssessmentResult.attempt_id` |
| Course to ContentItem          | 1:N           | `ContentItem.course_id`              |
| Skill to ContentSkill          | 1:N           | `ContentSkill.skill_id`              |
| ContentItem to ContentSkill    | 1:N           | `ContentSkill.content_id`            |
| ContentItem to Skill           | N:M           | `ContentSkill` bridge entity         |
| Skill to prerequisite Skill    | N:M           | `SkillPrerequisite`                  |
| Learner to LearningPath        | 1:N           | `LearningPath.learner_id`            |
| Course to LearningPath         | 1:N           | `LearningPath.course_id`             |
| Learner to Recommendation      | 1:N           | `Recommendation.learner_id`          |
| ContentItem to Recommendation  | 1:N           | `Recommendation.content_id`          |
| LearningPath to Recommendation | 1:N, optional | `Recommendation.learning_path_id`    |

---

# 13. Required Edge Cases and Expected Outcomes

| ID     | Edge case                              | Expected outcome                                                                           |
| ------ | -------------------------------------- | ------------------------------------------------------------------------------------------ |
| EC-001 | Recommendation violates a prerequisite | Reject or exclude the ineligible recommendation and record a reason code                   |
| EC-002 | Attempt timestamps are invalid         | Flag the record as invalid; do not silently correct its timestamps                         |
| EC-003 | Content maps to a nonexistent skill    | Detect the missing reference and report a foreign-key integrity error                      |
| EC-004 | Mastery uses a future attempt          | Fail the temporal validation; exclude information occurring after the evaluation timestamp |
| EC-005 | Learning path loops without progress   | Detect repeated no-progress transitions and record an anomaly                              |

Deliberate anomaly fixtures must be isolated from valid baseline data. Each should have an explicit `issue_type` or ground-truth label.

---

# 14. Derived Values and Reconciliation

Derived values must be calculated from source records rather than generated independently.

Examples:

* Assessment percentage is derived from score and maximum score.
* Pass/fail status is derived from the configured passing threshold.
* Skill mastery is derived from relevant historical assessment results and content-skill weights.
* Recommendation eligibility is derived from learner status, content status, mastery, and prerequisites.
* Recommendation outcomes are derived from subsequent learner events.
* Dataset totals must reconcile with the actual generated records.

Every calculation should have documented assumptions and validation tests.

---

# 15. Reproducibility and Data Provenance

The synthetic-data generator must use a fixed, configurable seed.

The current configured seed is `20261022`.

Reproducibility verification should:

1. Generate the dataset twice using identical settings.
2. Compare row counts for every entity.
3. Compare deterministic IDs.
4. Compare file checksums after normalizing any intentionally variable metadata.
5. Record the generation command, seed, configuration, validation results, and source manifest.

If external data is introduced, document the source URL, version, retrieval date, license, attribution, transformations, and discarded fields.

External data is optional; synthetic data is suitable for this project.

---

# 16. Implementation Verification Note

This document describes the expected schema and validation contract. Before submission, compare every field, constraint, relationship, and lifecycle rule against the actual SQLAlchemy models and application logic.

If an expected rule is not implemented, document it as incomplete or implement and test it before claiming full compliance.

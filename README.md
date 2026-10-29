# AI-Powered Personalized Learning Recommendation System

A Python-based learning recommendation system that personalizes educational content using learner mastery, assessment history, skill prerequisites, content difficulty, and learning progress.

The project includes synthetic dataset generation, prerequisite-aware recommendation logic, learning path management, REST API endpoints, data integrity validation, ground-truth evaluation, and automated tests.

---

## 1. Project Overview

Learners have different skill levels, learning speeds, assessment results, and prerequisite knowledge. Recommending the same content to every learner may result in activities that are either too easy or too difficult.

The **AI-Powered Personalized Learning Recommendation System** addresses this problem by analyzing learner assessment history and skill mastery to identify suitable learning activities.

The system evaluates content eligibility, checks prerequisite requirements, excludes previously completed activities, and ranks eligible content using a deterministic scoring approach.

It also supports learning path creation, historical recommendation records, synthetic data generation, and API-based access.

### Project Objectives

* Generate personalized learning recommendations.
* Calculate learner skill mastery from assessment history.
* Enforce skill prerequisite requirements.
* Rank eligible learning activities.
* Create and retrieve learning paths.
* Preserve recommendation history and decision reason codes.
* Validate dataset integrity and relationships.
* Evaluate recommendation behavior against predefined ground-truth scenarios.
* Provide REST API endpoints for application integration.

---

## 2. Key Features

### 2.1 Personalized Recommendations

Recommends published learning activities based on learner skill mastery, content difficulty, and skill mapping contribution weights.

### 2.2 Skill Mastery Analysis

Calculates skill mastery from assessment history. Historical mastery calculations can use an evaluation timestamp to exclude assessments recorded after that time.

### 2.3 Prerequisite Validation

Checks whether the learner has achieved the required mastery of prerequisite skills before recommending dependent content.

### 2.4 Learning Path Management

Creates learning paths for active learners enrolled in published courses. Existing active paths for the same learner and course are reused to prevent duplicate active paths.

### 2.5 Learner Status Validation

Prevents inactive learners from receiving recommendations.

### 2.6 Content Eligibility Validation

Filters out content that is not published, content that was not yet available at the evaluation time, and content the learner has already completed.

### 2.7 Explainable Recommendations

Attaches reason codes to recommendations, including:

* `LOW_SKILL_MASTERY`
* `SKILL_DEVELOPMENT`
* `PREREQUISITE_NOT_MASTERED`
* `CONTINUE_SKILL_DEVELOPMENT`

Reason codes help explain recommendation decisions.

### 2.8 Historical Recommendation Records

Supports saving recommendation records with identifiers, timestamps, mastery information, decisions, and reason codes.

### 2.9 Synthetic Dataset Generation

Generates development and full datasets using configurable dataset sizes and a fixed random seed.

### 2.10 Data Integrity Validation

Checks database relationships, assessment score consistency, timestamps, attempt lifecycle states, prerequisite relationships, duplicate attempt-number combinations, and other integrity conditions.

### 2.11 Ground-Truth Evaluation

Evaluates recommendation behavior against predefined scenarios representing expected recommendation outcomes.

### 2.12 REST API

Exposes functionality through FastAPI endpoints and interactive Swagger documentation.

### 2.13 Automated Testing

Uses pytest to test data integrity, mastery calculations, temporal behavior, and recommendation rules.

### 2.14 Dataset Exports

Supports exporting supported database tables into CSV and JSON files, along with an SQL database dump and a manifest containing row counts and SHA-256 checksums.

---

## 3. Technology Stack

| Technology | Purpose                                            |
| ---------- | -------------------------------------------------- |
| Python     | Core programming language                          |
| FastAPI    | REST API development                               |
| SQLAlchemy | ORM and database interaction                       |
| SQLite     | Relational database                                |
| NumPy      | Synthetic data generation and numerical operations |
| Pandas     | Data analysis and data processing support          |
| Pytest     | Automated testing                                  |
| Uvicorn    | ASGI server for running the API                    |
| JSON       | Ground-truth scenarios and structured exports      |
| CSV        | Tabular dataset exports                            |
| SQL        | Database schema and data export                    |
| Git/GitHub | Source control and repository hosting              |

---

## 4. Project Structure

The following structure highlights the main project files. Additional scripts, tests, configuration files, and export artifacts may also exist.

```text
ai-powered-learning-recommender/
│
├── ai_usage/
│   └── prompt_history.md
│
├── api/
│   ├── __init__.py
│   └── main.py
│
├── config/
│   └── settings.py
│
├── data/
│   └── ground_truth.json
│
├── docs/
│   └── data_dictionary.md
│
├── scripts/
│   ├── generate_data.py
│   └── validate_data.py
│
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── data_generator.py
│   ├── evaluation.py
│   ├── learning_paths.py
│   ├── mastery.py
│   ├── models.py
│   ├── recommender.py
│   ├── validation.py
│   └── validator.py
│
├── tests/
│   ├── test_anomalies.py
│   ├── test_data_integrity.py
│   ├── test_mastery.py
│   ├── test_recommendation_rules.py
│   └── test_recommendations.py
│
├── exports/
│   ├── learners.csv
│   ├── learners.json
│   ├── courses.csv
│   ├── courses.json
│   ├── skills.csv
│   ├── skills.json
│   ├── content_items.csv
│   ├── content_items.json
│   ├── attempts.csv
│   ├── attempts.json
│   ├── assessment_results.csv
│   ├── assessment_results.json
│   ├── learning_full.sql
│   └── manifest.json
│
├── generate_dev_data.py
├── generate_full_data.py
├── export_dataset.py
├── verify_sql_export.py
├── verify_full_data.py
├── validate_dev_data.py
├── run_evaluation.py
├── requirements.txt
├── README.md
└── .gitignore
```

The `exports/` directory contains generated artifacts. Its exact contents depend on which tables are present in the source database.

The database files are generated locally and should not be confused with the source code or the exported datasets.

---

## 5. Installation and Setup

### 5.1 Prerequisites

* Python 3.13 or a compatible Python version
* pip
* Visual Studio Code or another Python editor
* A terminal such as PowerShell
* Sufficient disk space for dataset generation and exports

### 5.2 Open the Project Directory

Open the project folder in Visual Studio Code.

Open a terminal in the project root directory.

### 5.3 Create a Virtual Environment

```powershell
python -m venv venv
```

### 5.4 Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If activation is blocked by your PowerShell execution policy, follow the appropriate policy guidance for your environment.

### 5.5 Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5.6 Verify the Installation

Check the Python version:

```powershell
python --version
```

Check for broken package requirements:

```powershell
python -m pip check
```

A successful dependency check should report:

```text
No broken requirements found.
```

---

## 6. Configuration and Reproducibility

Project configuration is maintained in:

```text
config/settings.py
```

The current configuration uses the following fixed seed and dataset sizes.

| Configuration | Development | Full Dataset |
| ------------- | ----------: | -----------: |
| Random seed   |    20261022 |     20261022 |
| Learners      |         100 |       10,000 |
| Courses       |          10 |          100 |
| Skills        |          50 |          500 |
| Content items |         100 |        2,000 |
| Attempts      |       5,000 |      500,000 |

Additional settings include:

* `ID_YEAR = 2026`
* `MAX_SCORE = 100`
* `PASSING_THRESHOLD = 70`

The fixed seed is intended to support repeatable synthetic data generation.

**Important:** A fixed seed alone does not prove that every output file is byte-for-byte reproducible. Reproducibility should be verified by generating data in a clean environment twice and comparing record counts and checksums.

The full-data generation script uses a separate database, `learning_full.db`, and stops if that database already contains learners. This protects against accidentally appending duplicate full datasets.

Do not run data-generation scripts against existing databases without first understanding their behavior and preserving any data you need.

---

## 7. Generate and Validate Data

### 7.1 Generate the Development Dataset

```powershell
python generate_dev_data.py
```

The development dataset is smaller and is intended for testing application behavior.

### 7.2 Validate the Development Dataset

```powershell
python validate_dev_data.py
```

This checks record counts and data integrity conditions.

### 7.3 Generate the Full Dataset

```powershell
python generate_full_data.py
```

The full-data generator uses the configured full dataset sizes and writes to:

```text
learning_full.db
```

**Warning:** The generator intentionally stops if the full database already contains learners. Do not delete or overwrite an existing database just to rerun the generator.

### 7.4 Verify the Full Dataset

```powershell
python verify_full_data.py
```

The verification script checks the expected record counts for the principal tables.

### 7.5 Latest Verified Full Dataset Counts

The full dataset verification previously passed with the following results:

| Table              | Expected Records |
| ------------------ | ---------------: |
| Learners           |           10,000 |
| Courses            |              100 |
| Skills             |              500 |
| Content items      |            2,000 |
| Attempts           |          500,000 |
| Assessment results |          500,000 |

The exported dataset also contained:

| Table                  | Exported Records |
| ---------------------- | ---------------: |
| Skill prerequisites    |              499 |
| Content-skill mappings |            2,000 |
| Learning paths         | 0 at export time |
| Recommendations        | 0 at export time |

Learning paths and recommendations can be created through application workflows. Their being empty in the generated full dataset does not, by itself, indicate a failure in the recommendation logic.

These counts represent observed verification results, not a guarantee that the database will retain the same counts after subsequent changes.

---

## 8. Dataset Exports

The project includes an export script that reads the existing full SQLite database and creates CSV, JSON, and SQL exports.

### 8.1 Generate the Exports

Run:

```powershell
python export_dataset.py
```

The script reads:

```text
learning_full.db
```

It creates the following directory:

```text
exports/
```

### 8.2 Exported Files

The export directory contains supported table exports in CSV and JSON formats, as well as:

| File                      | Purpose                                                               |
| ------------------------- | --------------------------------------------------------------------- |
| `learning_full.sql`       | SQLite schema and data dump                                           |
| `manifest.json`           | Source database, random seed, table row counts, and SHA-256 checksums |
| `learners.csv`            | Learner records                                                       |
| `learners.json`           | Learner records in JSON format                                        |
| `attempts.csv`            | Attempt records                                                       |
| `attempts.json`           | Attempt records in JSON format                                        |
| `assessment_results.csv`  | Assessment result records                                             |
| `assessment_results.json` | Assessment result records in JSON format                              |

Additional CSV and JSON files are generated for the other supported tables.

### 8.3 Verify CSV Row Counts

The CSV export verification procedure compares each CSV file's number of data rows with the corresponding row count recorded in `manifest.json`.

The latest verification passed for all exported CSV files.

### 8.4 Validate the Manifest

Run:

```powershell
python -m json.tool exports\manifest.json
```

This checks whether the manifest is valid JSON and displays its contents.

### 8.5 Test SQL Restoration

Run:

```powershell
python verify_sql_export.py
```

This script restores the SQL dump into a separate verification database and checks expected record counts and foreign-key integrity.

The latest restore test passed for the six principal dataset tables and reported no foreign-key violations.

The test database is created under `exports/` and is separate from the original full database.

### 8.6 Export Size and GitHub Considerations

The full SQL export was approximately 125.65 MB.

GitHub normally rejects individual files larger than 100 MiB. Therefore, do not commit this SQL file directly to a normal GitHub repository.

For a public submission, consider one of these approaches:

* Publish the export script and a smaller sample dataset.
* Provide compressed exports where appropriate.
* Store large artifacts in an approved external location if permitted by the challenge.
* Document how evaluators can generate the full dataset locally.

Do not claim that an export is available in the public repository unless it has actually been uploaded.

---

## 9. Run the API

The project uses FastAPI to expose recommendation-related functionality.

### 9.1 Start the API

Run:

```powershell
python -m uvicorn api.main:app --reload
```

Keep the terminal open while using the API.

### 9.2 Open Swagger Documentation

With the server running, open:

http://127.0.0.1:8000/docs

Swagger allows you to inspect endpoints, view parameters, and submit requests.

### 9.3 Check the Application

Open:

http://127.0.0.1:8000/

### 9.4 Check API Health

Open:

http://127.0.0.1:8000/health

---

## 10. API Endpoints

The application exposes the following endpoints.

| Method | Endpoint                                                      | Description                            |
| ------ | ------------------------------------------------------------- | -------------------------------------- |
| GET    | `/`                                                           | Checks the application                 |
| GET    | `/health`                                                     | Checks API health                      |
| GET    | `/learners/{learner_id}/mastery`                              | Retrieves learner skill mastery        |
| GET    | `/learners/{learner_id}/recommendations`                      | Retrieves personalized recommendations |
| POST   | `/learners/{learner_id}/learning-paths`                       | Creates or retrieves a learning path   |
| GET    | `/learners/{learner_id}/courses/{course_id}/learning-content` | Retrieves eligible learning content    |

Use the Swagger documentation at `/docs` to inspect request parameters and test each endpoint.

Actual responses depend on the database contents, learner status, course status, assessment history, and prerequisite relationships.

---

## 11. Recommendation Workflow

The recommendation workflow follows these main steps.

1. Retrieve the learner and check the learner's status.
2. Establish the evaluation timestamp.
3. Calculate skill mastery from assessment history.
4. Identify published content available at the evaluation time.
5. Exclude content completed by the learner before that time.
6. Retrieve the skills associated with each content item.
7. Check that the mapped skills are active.
8. Evaluate prerequisite mastery.
9. Exclude content that violates prerequisite requirements.
10. Calculate recommendation scores for eligible content.
11. Attach reason codes explaining the recommendation.
12. Rank recommendations by score, with deterministic content-ID tie-breaking.
13. Return the requested number of recommendations.
14. Save recommendation history when the save operation is invoked.

The system uses a rule-based scoring mechanism. It should not be described as a trained machine-learning recommendation model unless a separate trained model is actually implemented.

---

## 12. Learning Path Management

Learning paths help organize eligible learning content for a learner and course.

### Learning Path Creation

The application checks:

* Whether the learner exists.
* Whether the learner is active.
* Whether the course exists.
* Whether the course is published.
* Whether an active learning path already exists for the learner and course.

If an active path exists, the existing path is returned. Otherwise, the application creates a new path.

### Learning Content Retrieval

The learning-content workflow filters published course content, excludes previously completed content, checks mapped skills, and evaluates prerequisite mastery.

Eligible content is ordered by difficulty and mastery-related information.

### Verification

A development-database test confirmed that the learning-path creation function returned the same learning path ID on two consecutive calls for the same learner and course.

This verifies duplicate prevention for the tested scenario, but does not establish concurrency safety under simultaneous requests.

---

## 13. Run Automated Tests

Run the test suite:

```powershell
python -m pytest -v
```

### Latest Verified Results

The latest recorded test run produced:

* Tests collected: **11**
* Tests passed: **11**
* Tests failed: **0**
* Deprecation warnings: **18**

The warnings relate to the use of `datetime.utcnow()` in SQLAlchemy model defaults. They did not cause the tests to fail.

The tests cover areas including:

* Attempt and assessment-result relationships.
* Assessment score validity.
* Attempt timestamp validity.
* Historical mastery calculations.
* Exclusion of future assessments from historical mastery.
* Unknown learner handling.
* Inactive learner recommendation behavior.
* Archived content exclusion.
* Recommendation eligibility for active learners.

Some test files in the repository may be empty or contain no collected tests. The reported total reflects tests collected by pytest, not the number of test files.

Run the suite again after changing the code to verify the current behavior.

---

## 14. Run Ground-Truth Evaluation

Execute the evaluation script:

```powershell
python run_evaluation.py
```

The evaluator compares recommendation behavior with predefined expected outcomes in:

```text
data/ground_truth.json
```

### Latest Verified Evaluation Results

| Metric          | Result |
| --------------- | -----: |
| Total scenarios |      8 |
| Evaluated       |      8 |
| Passed          |      8 |
| Failed          |      0 |
| Pass rate       |   100% |

The eight scenarios cover:

1. Beginner learners receiving foundational content.
2. Learners who have mastered fundamentals progressing to advanced content.
3. Learners who have not mastered prerequisites.
4. Inactive learners receiving no recommendations.
5. Advanced learners receiving suitable advanced content.
6. Learners with low assessment scores receiving remedial content.
7. Learners with high assessment scores receiving next-level content.
8. Archived content being excluded from recommendations.

A 100% pass rate means all eight defined scenarios passed. It does not prove that every possible real-world learning scenario has been tested.

Run the evaluation again after changing recommendation logic.

---

## 15. Data Validation

The project includes validation scripts for checking database records and relationships.

Run development data validation:

```powershell
python validate_dev_data.py
```

Run full dataset verification:

```powershell
python verify_full_data.py
```

The broader validator checks conditions such as:

* Required tables contain data.
* Content references valid courses.
* Content-skill mappings reference existing content and skills.
* Attempt timestamps and lifecycle states are consistent.
* Every attempt has an assessment result.
* Assessment results reference existing attempts.
* Assessment scores and percentages are valid and consistent.
* Attempts reference existing learners and content.
* Prerequisite relationships reference valid skills.
* Active prerequisite relationships do not form cycles.
* Attempt-number combinations are not duplicated.
* Learning paths reference valid learners and courses.
* Recommendations reference valid related records.

### Important Limitations

Validation scripts check the conditions implemented in the code. They do not automatically establish correctness for every possible business rule.

For example, reconstructing a learner's exact historical state may require additional history tables when content publication status or attempt lifecycle status changes over time.

The current full dataset verification focuses on expected record counts for the principal tables. Run the appropriate validation scripts after regenerating or modifying data.

---

## 16. Design Decisions and Trade-Offs

### 16.1 Synthetic Data

Synthetic data allows the system to be tested at a larger scale without depending on access to private learner records.

**Trade-off:** Synthetic data can validate application behavior and data integrity, but it cannot establish that recommendations improve learning outcomes for real learners.

### 16.2 SQLite

SQLite provides a simple, portable relational database suitable for local development and evaluation.

**Trade-off:** A production deployment with many concurrent users may require a server-based database and additional operational controls.

### 16.3 Rule-Based Recommendation Scoring

Recommendation scores are calculated from skill gaps, content difficulty, and mapping contribution weights.

**Trade-off:** This approach is explainable and deterministic, but the scoring rules may not capture every learner preference or predict actual learning success.

### 16.4 Prerequisite Enforcement

Prerequisite checks prevent dependent content from being recommended when required prerequisite mastery is insufficient.

**Trade-off:** Incorrect or overly strict prerequisite definitions may prevent otherwise useful content from being recommended.

### 16.5 Historical Evaluation

The recommendation logic supports an evaluation timestamp for excluding assessments and certain changes that occur after the evaluation time.

**Trade-off:** Full historical reconstruction is limited when the database does not preserve complete temporal histories for every changing entity or lifecycle status.

### 16.6 Recommendation History

Recommendations can be saved as separate historical records instead of overwriting earlier recommendations.

**Trade-off:** Historical storage increases database size and requires retention, querying, and lifecycle policies as the application grows.

---

## 17. Limitations and Future Improvements

The current implementation is a prototype and can be improved in several areas.

### Potential Improvements

* Add user authentication and authorization.
* Expand automated tests for edge cases and negative scenarios.
* Add temporal evaluation metrics and more comprehensive offline recommendation metrics.
* Introduce recommendation feedback and outcome tracking.
* Improve ranking using validated learner feedback.
* Add structured logging and monitoring.
* Add concurrency-safe learning-path creation.
* Improve historical reconstruction of content status and attempt lifecycle changes.
* Add a documented, automated reproducibility comparison.
* Improve API error handling and request validation.
* Add deployment configuration for a production environment.
* Evaluate the system with real, appropriately governed learner data if available.

---

## 18. AI Usage and Development Process

AI assistance was used during development for planning, implementation guidance, code review, test design, debugging, and documentation.

The candidate remains responsible for reviewing the implementation, understanding the recommendation logic, and validating the resulting code.

AI-generated suggestions should not be treated as automatically correct. They must be checked against the project requirements and verified through execution and testing.

The project includes an AI usage record at:

```text
ai_usage/prompt_history.md
```

That file should document representative prompts, the resulting assistance, human review, modifications, and validation outcomes.

Only claim that a suggestion was tested or accepted when the corresponding work was actually completed.

---

## 19. Reproducibility and Verification Status

The following checks have been completed during development:

| Check                                | Recorded Result                          |
| ------------------------------------ | ---------------------------------------- |
| Full dataset record counts           | Passed                                   |
| Development dataset validation       | Passed                                   |
| CSV row-count verification           | Passed                                   |
| JSON manifest parsing                | Passed                                   |
| SQL export restoration               | Passed                                   |
| SQL foreign-key check                | No violations                            |
| Automated tests                      | 11 passed                                |
| Ground-truth evaluation              | 8/8 passed                               |
| Recommendation generation and saving | Passed for the tested learner            |
| Learning-path creation               | Passed for the tested learner and course |

These results reflect the recorded development runs. Re-run the relevant commands after code changes before submitting.

**Full deterministic reproducibility has not yet been established solely by these checks.** To claim reproducibility, generate the dataset twice in clean, separate locations with the same seed and configuration, then compare table counts and checksums.

---

## 20. Troubleshooting

### Python Cannot Find a Script

Confirm that the file exists in the project root:

```powershell
Test-Path .\export_dataset.py
```

If the result is `False`, create or save the file in the correct folder.

### Dependencies Are Missing

Activate the virtual environment and run:

```powershell
python -m pip install -r requirements.txt
```

### API Does Not Start

Check that the virtual environment is active, dependencies are installed, and the terminal is in the project root.

Then run:

```powershell
python -m uvicorn api.main:app --reload
```

### The Full Dataset Generator Stops

The generator stops when `learning_full.db` already contains learners. This is intentional protection against duplicate generation.

Do not delete the database automatically. Inspect and preserve existing data before deciding how to proceed.

### CSV or SQL Exports Are Missing

Run:

```powershell
python export_dataset.py
```

Then verify the manifest and exported files before proceeding.

### SQL Restore Test Reports an Existing Database

The restore verification script deliberately avoids overwriting an existing test database. Confirm that the file is only a disposable verification artifact before renaming or removing it.

### Git Is Not Recognized

If PowerShell reports that `git` is not recognized, Git may not be installed or available on the current PATH.

Install Git for Windows or use GitHub Desktop or Visual Studio Code's Source Control interface. Verify that your repository is public before sharing its URL with the evaluator.

---

## 21. Conclusion

The AI-Powered Personalized Learning Recommendation System demonstrates a rule-based approach to personalized educational content recommendations using learner mastery, assessment history, skill prerequisites, content difficulty, and learning progress.

The project includes synthetic data generation, relational data validation, recommendation scoring, learning path management, historical recommendation records, REST API endpoints, automated tests, ground-truth evaluation, and CSV/JSON/SQL export functionality.

The implementation provides a foundation for further work on recommendation quality, temporal correctness, reproducibility, scalability, and real-world learning outcome evaluation.

The latest recorded development checks passed, including 11 automated tests, eight ground-truth scenarios, development data validation, CSV export verification, and SQL restoration.

These results support the current implementation, while further reproducibility testing and the remaining submission checks should be completed before final delivery.

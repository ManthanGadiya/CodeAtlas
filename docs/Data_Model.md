# CodeAtlas — Data Model

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define the data architecture required to observe the student's coding behavior, represent knowledge and mistakes, track learning over time, and power the adaptive tutoring system.

---

# 1. Purpose

CodeAtlas is fundamentally an **evidence-driven learning system**.

Almost every intelligent decision depends on data:

```text
What did the student do?
        ↓
What happened?
        ↓
What mistake occurred?
        ↓
What does this reveal about the student?
        ↓
What should happen next?
````

Therefore the data model must preserve both:

```text
Raw Evidence
```

and:

```text
Derived Understanding
```

The system must never replace raw evidence with AI-generated conclusions.

---

# 2. Core Data Principle

CodeAtlas follows:

> **Store observations first. Derive interpretations second.**

For example:

Bad:

```text
Student is bad at recursion.
```

Better:

```text
Student failed recursion problem 184.
Student requested 2 hints.
Student made a recursive-state mistake.
Student solved the corrected version after guidance.
Student failed a novel recursion problem 4 days later.
```

The second representation allows the system to change its interpretation when new evidence appears.

---

# 3. Data Architecture

```text
                    ┌──────────────────┐
                    │      Student     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Sessions     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Events      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
          Code Data      Test Data      AI Events
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │ Evidence Layer   │
                    └────────┬─────────┘
                             ▼
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Mistake Model   Skill Model   Behavior Model
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │  Student State   │
                    └────────┬─────────┘
                             ▼
                    ┌──────────────────┐
                    │ Adaptive Engine  │
                    └──────────────────┘
```

---

# 4. Data Layers

The database should conceptually contain five layers.

```text
Layer 1 — Identity
Layer 2 — Raw Interaction Data
Layer 3 — Evidence
Layer 4 — Student Models
Layer 5 — Adaptive Decisions
```

---

# 5. Layer 1 — Identity

Contains:

```text
Student
Account
Preferences
Settings
```

Because CodeAtlas initially targets one student, the architecture should still support multiple users in the future.

---

# 6. Student Entity

Conceptual structure:

```text
Student
{
    id,
    created_at,
    updated_at,
    timezone,
    preferred_language,
    status
}
```

Example:

```text
student_id:
stu_001
```

---

# 7. Student Preferences

Preferences should be separated from learning state.

Example:

```text
StudentPreferences
{
    student_id,
    preferred_language,
    preferred_difficulty,
    explanation_style,
    hint_style,
    session_length,
    notification_preferences
}
```

A preference is not evidence of ability.

---

# 8. Learning State

The current inferred state should be separate.

```text
StudentLearningState
{
    student_id,
    overall_mastery,
    learning_velocity,
    independence_score,
    retention_score,
    updated_at
}
```

This is derived data.

---

# 9. Session

A session represents a continuous learning interaction.

```text
Session
{
    id,
    student_id,
    started_at,
    ended_at,
    session_type,
    device_context
}
```

Examples:

```text
practice
debugging
diagnostic
revision
retrieval
free_coding
```

---

# 10. Event

The event is the most important raw entity.

Every meaningful interaction should produce an event.

```text
Event
{
    id,
    student_id,
    session_id,
    event_type,
    timestamp,
    payload
}
```

---

# 11. Event Types

Possible events:

```text
PROBLEM_OPENED
CODE_TYPED
CODE_SAVED
CODE_RUN
TEST_CREATED
TEST_EXECUTED
COMPILATION_FAILED
RUNTIME_FAILED
TEST_FAILED
TEST_PASSED
HINT_REQUESTED
HINT_SHOWN
CODE_REVISED
SOLUTION_REVEALED
PROBLEM_COMPLETED
PROBLEM_ABANDONED
EXPLANATION_REQUESTED
EXPLANATION_SUBMITTED
RETRIEVAL_ATTEMPTED
```

---

# 12. Why Events Matter

Suppose the student eventually solves a problem.

A simple database may store:

```text
Solved = true
```

CodeAtlas needs much more:

```text
Time
Attempts
Hints
Errors
Revisions
Tests
AI interactions
```

Therefore:

> **The event stream is the historical truth of CodeAtlas.**

---

# 13. Event Immutability

Events should generally be immutable.

Instead of:

```text
Changing an old event
```

prefer:

```text
Original Event
+
Correction Event
```

This creates an auditable history.

---

# 14. Code Artifact

Every meaningful version of student code should be represented.

```text
CodeArtifact
{
    id,
    student_id,
    problem_id,
    session_id,
    language,
    source_code,
    created_at,
    parent_artifact_id
}
```

---

# 15. Code Version Graph

Code revisions form a graph:

```text
Version 1
    │
    ├── Version 2
    │      │
    │      └── Version 3
    │
    └── Version 2b
```

This is better represented using:

```text
parent_artifact_id
```

than storing only the final code.

---

# 16. Code Diff

A revision should optionally store:

```text
CodeDiff
{
    artifact_before,
    artifact_after,
    added_lines,
    removed_lines,
    changed_lines,
    diff_text
}
```

This allows CodeAtlas to study debugging behavior.

---

# 17. Execution

Every code execution should produce an execution record.

```text
Execution
{
    id,
    code_artifact_id,
    timestamp,
    status,
    runtime_ms,
    memory_bytes,
    exit_code,
    stdout,
    stderr
}
```

---

# 18. Execution Status

Possible states:

```text
SUCCESS
COMPILE_ERROR
RUNTIME_ERROR
TIMEOUT
MEMORY_LIMIT
SYSTEM_ERROR
```

---

# 19. Test Case

```text
TestCase
{
    id,
    problem_id,
    input,
    expected_output,
    test_type
}
```

Test types:

```text
NORMAL
EDGE
BOUNDARY
NEGATIVE
RANDOM
STRESS
HIDDEN
```

---

# 20. Test Execution

```text
TestExecution
{
    id,
    execution_id,
    test_case_id,
    actual_output,
    expected_output,
    passed,
    runtime_ms
}
```

---

# 21. Problem

A problem is the learning activity given to the student.

```text
Problem
{
    id,
    title,
    description,
    language,
    source_type,
    difficulty,
    estimated_time,
    created_at
}
```

---

# 22. Problem Source

Possible values:

```text
CURATED
GENERATED
ADAPTED
DIAGNOSTIC
RETRIEVAL
TRANSFER
```

This distinction matters when evaluating generated content.

---

# 23. Problem Difficulty

Difficulty should not be a single unexplained number.

Represent:

```text
ProblemDifficulty
{
    problem_id,
    overall,
    conceptual,
    implementation,
    reasoning,
    debugging,
    confidence,
    model_version
}
```

---

# 24. Difficulty Evolution

Difficulty estimates can change as evidence accumulates.

Therefore:

```text
ProblemDifficultyHistory
```

should optionally record:

```text
old_value
new_value
reason
model_version
timestamp
```

---

# 25. Skill

A skill represents a programming capability.

```text
Skill
{
    id,
    name,
    description,
    domain,
    parent_skill_id
}
```

---

# 26. Skill Hierarchy

Example:

```text
Algorithms
│
├── Searching
│   └── Binary Search
│       ├── Boundary Handling
│       ├── Search Space Reduction
│       └── Invariants
│
└── Dynamic Programming
    ├── State Definition
    ├── Transition
    └── Memoization
```

This allows subskill-level personalization.

---

# 27. Skill Relationships

Skills can also have prerequisites.

```text
SkillRelationship
{
    source_skill_id,
    target_skill_id,
    relationship_type,
    strength
}
```

Relationship types:

```text
PREREQUISITE
RELATED
COMPOSES
GENERALIZES
SPECIALIZES
```

---

# 28. Problem-Skill Mapping

A problem may test multiple skills.

```text
ProblemSkill
{
    problem_id,
    skill_id,
    importance,
    role
}
```

Example:

```text
Binary Search Problem

Binary Search        → primary
Arrays                → supporting
Complexity Analysis   → supporting
```

---

# 29. Student-Skill State

This represents the current belief about the student.

```text
StudentSkillState
{
    student_id,
    skill_id,
    mastery,
    confidence,
    retention,
    evidence_count,
    last_practiced_at,
    updated_at
}
```

---

# 30. Student-Skill State Is Derived

Never treat:

```text
mastery = 0.63
```

as raw truth.

It should be reproducible from evidence and model version.

Therefore store:

```text
model_version
calculated_at
```

---

# 31. Mastery History

Track how mastery changes.

```text
MasterySnapshot
{
    student_id,
    skill_id,
    mastery,
    confidence,
    reason,
    model_version,
    timestamp
}
```

Example:

```text
0.32
  ↓
0.45
  ↓
0.58
  ↓
0.51
  ↓
0.69
```

A decrease is valid.

---

# 32. Evidence

Evidence connects observations to inferred states.

```text
Evidence
{
    id,
    student_id,
    source_event_id,
    skill_id,
    evidence_type,
    value,
    confidence,
    timestamp
}
```

---

# 33. Evidence Types

Examples:

```text
CORRECT_SOLUTION
INCORRECT_SOLUTION
DELAYED_RETRIEVAL
TRANSFER_SUCCESS
TRANSFER_FAILURE
HINT_DEPENDENCY
INDEPENDENT_SUCCESS
REPEATED_MISTAKE
EXPLANATION_SUCCESS
```

---

# 34. Mistake

```text
Mistake
{
    id,
    student_id,
    problem_id,
    code_artifact_id,
    category_id,
    severity,
    confidence,
    detected_at
}
```

---

# 35. Mistake Taxonomy Reference

Mistake categories should not be stored as arbitrary strings.

Use:

```text
MistakeCategory
{
    id,
    name,
    description,
    parent_id
}
```

Examples:

```text
Syntax Error
Logic Error
Off-by-One
Wrong Algorithm
Complexity Mistake
Requirement Misunderstanding
Repeated Mistake
Copying Solution
Overengineering
```

---

# 36. Mistake Evidence

Every classification should store evidence.

```text
MistakeEvidence
{
    mistake_id,
    evidence_type,
    evidence,
    confidence
}
```

Example:

```text
Evidence:
Loop executes one iteration beyond array boundary.

Confidence:
0.94
```

---

# 37. Mistake Recurrence

A recurring mistake should be represented explicitly.

```text
MistakePattern
{
    id,
    student_id,
    category_id,
    skill_id,
    occurrence_count,
    first_seen_at,
    last_seen_at,
    recurrence_rate,
    confidence
}
```

---

# 38. Behavior

Behavioral observations should be separate from mistakes.

```text
BehaviorObservation
{
    id,
    student_id,
    session_id,
    behavior_type,
    value,
    confidence,
    timestamp
}
```

---

# 39. Behavior Types

Examples:

```text
RUSHING
OVERENGINEERING
LOW_TESTING
HINT_DEPENDENCY
RANDOM_EDITING
EARLY_SOLUTION_REVEAL
PERSISTENCE
ABANDONMENT
REPEATED_RETRY
```

---

# 40. Behavior Pattern

Aggregated behavior:

```text
BehaviorPattern
{
    student_id,
    behavior_type,
    frequency,
    severity,
    trend,
    confidence,
    last_observed_at
}
```

---

# 41. Hint

```text
Hint
{
    id,
    problem_id,
    level,
    content,
    generated_by,
    created_at
}
```

---

# 42. Hint Request

```text
HintRequest
{
    id,
    student_id,
    problem_id,
    session_id,
    hint_id,
    requested_at,
    time_since_attempt_start
}
```

This allows CodeAtlas to study when the student asks for help.

---

# 43. Tutor Interaction

All AI interactions should be recorded.

```text
TutorInteraction
{
    id,
    student_id,
    session_id,
    problem_id,
    interaction_type,
    model_provider,
    model_name,
    model_version,
    prompt_context_hash,
    response,
    latency_ms,
    timestamp
}
```

---

# 44. Do Not Store Every Prompt Blindly

AI conversations may contain:

```text
source code
personal information
secrets
```

Therefore storage policies must be configurable.

Possible approach:

```text
Raw prompt
→ temporary storage

Structured result
→ persistent storage
```

---

# 45. AI Analysis

LLM-generated analysis should be represented separately.

```text
AIAnalysis
{
    id,
    source_event_id,
    analysis_type,
    result,
    confidence,
    model,
    model_version,
    created_at
}
```

---

# 46. AI Analysis Types

```text
MISTAKE_CLASSIFICATION
CODE_ANALYSIS
BEHAVIOR_ANALYSIS
HINT_EVALUATION
EXPLANATION_EVALUATION
DIFFICULTY_ESTIMATION
PROBLEM_QUALITY
```

---

# 47. Model Version

Every model-derived value must identify its model.

```text
model_name
model_version
prompt_version
```

This is necessary for reproducibility.

---

# 48. Retrieval Event

When a skill is intentionally revisited:

```text
RetrievalAttempt
{
    id,
    student_id,
    skill_id,
    problem_id,
    scheduled_at,
    attempted_at,
    result,
    confidence
}
```

---

# 49. Retention State

```text
RetentionState
{
    student_id,
    skill_id,
    stability,
    retrieval_probability,
    last_successful_retrieval,
    next_recommended_review,
    model_version
}
```

---

# 50. Curriculum

```text
Curriculum
{
    id,
    name,
    description,
    version,
    created_at
}
```

---

# 51. Curriculum Node

```text
CurriculumNode
{
    curriculum_id,
    skill_id,
    sequence_order,
    prerequisite_level,
    status
}
```

This represents the theoretical curriculum.

---

# 52. Adaptive Curriculum

The student's personalized curriculum should be separate.

```text
StudentCurriculum
{
    student_id,
    curriculum_id,
    current_node,
    progression_state,
    updated_at
}
```

---

# 53. Curriculum Decision

Every major adaptive decision should be recorded.

```text
CurriculumDecision
{
    id,
    student_id,
    selected_problem_id,
    target_skill_id,
    decision_type,
    reason,
    confidence,
    model_version,
    created_at
}
```

---

# 54. Decision Alternatives

For explainability, optionally store:

```text
DecisionCandidate
{
    decision_id,
    candidate_id,
    expected_learning_gain,
    expected_success,
    retention_value,
    exploration_value
}
```

This allows CodeAtlas to explain why one problem was selected over another.

---

# 55. Learning Objective

Each problem should have explicit objectives.

```text
LearningObjective
{
    id,
    problem_id,
    skill_id,
    objective_type,
    description
}
```

Types:

```text
INTRODUCE
PRACTICE
RETRIEVE
TRANSFER
DEBUG
EXPLAIN
MASTER
```

---

# 56. Assessment

```text
Assessment
{
    id,
    student_id,
    type,
    started_at,
    completed_at,
    score
}
```

Types:

```text
DIAGNOSTIC
FORMATIVE
RETRIEVAL
TRANSFER
SUMMATIVE
```

---

# 57. Assessment Item

```text
AssessmentItem
{
    assessment_id,
    problem_id,
    order,
    response,
    score
}
```

---

# 58. Learning Outcome

An outcome should represent measurable change.

```text
LearningOutcome
{
    id,
    student_id,
    skill_id,
    baseline_mastery,
    final_mastery,
    mastery_gain,
    retention_gain,
    transfer_gain,
    measurement_period
}
```

---

# 59. Experiment

Future research requires controlled experiments.

```text
Experiment
{
    id,
    name,
    hypothesis,
    version,
    started_at,
    ended_at,
    status
}
```

---

# 60. Experiment Assignment

```text
ExperimentAssignment
{
    experiment_id,
    student_id,
    condition,
    assigned_at
}
```

---

# 61. Metric Observation

```text
MetricObservation
{
    id,
    student_id,
    metric_name,
    value,
    context,
    timestamp
}
```

Examples:

```text
independent_success_rate
hint_dependency
retention
transfer
learning_velocity
```

---

# 62. Audit Log

Important system operations should be auditable.

```text
AuditLog
{
    id,
    actor_type,
    actor_id,
    action,
    resource_type,
    resource_id,
    timestamp,
    metadata
}
```

---

# 63. Data Provenance

Every derived value should ideally be traceable:

```text
Derived State
     ↓
Model Version
     ↓
Evidence
     ↓
Original Events
```

This is critical for debugging the intelligence layer.

---

# 64. Raw vs Derived Data

The database should conceptually distinguish:

```text
RAW
├── events
├── code
├── executions
├── tests
└── interactions

DERIVED
├── mastery
├── behavior patterns
├── mistake patterns
├── retention
├── difficulty
└── recommendations
```

---

# 65. Event Sourcing Consideration

CodeAtlas should strongly consider an event-oriented architecture.

The source of truth becomes:

```text
Event Stream
```

while current states are projections:

```text
Events
 ↓
Projection
 ↓
Student State
```

---

# 66. Why Event Sourcing Fits CodeAtlas

Learning models will change.

Suppose version 1 calculates:

```text
Mastery = 0.62
```

Later version 2 improves the model.

The system should be able to:

```text
Replay historical evidence
```

and calculate:

```text
Mastery = 0.71
```

without losing the original data.

---

# 67. Database Strategy

Recommended initial database:

```text
PostgreSQL
```

because CodeAtlas needs:

```text
relational integrity
transactions
JSON support
indexing
analytics
vector extensions
```

---

# 68. Vector Storage

If embeddings are required:

```text
pgvector
```

can initially be preferred over introducing a separate vector database.

Store:

```text
embedding
embedding_model
embedding_version
source_type
source_id
```

---

# 69. Object Storage

Large artifacts should not necessarily live directly in PostgreSQL.

Potential storage:

```text
Object Storage
    ↓
source code snapshots
execution logs
large datasets
generated files
```

Database stores:

```text
metadata
reference
hash
```

---

# 70. Code Hashing

Every code artifact should have a content hash.

Example:

```text
SHA-256
```

Purpose:

```text
duplicate detection
integrity
version tracking
cache keys
```

---

# 71. Deduplication

Problems, code, and generated content should be checked for duplication.

Potential identifiers:

```text
content_hash
semantic_embedding
problem_template_id
```

---

# 72. Data Retention

Different data types may have different retention periods.

Example:

```text
Raw execution logs:
shorter retention

Student learning history:
longer retention

Aggregated metrics:
long-term

Security logs:
policy-defined
```

Exact policies belong in:

```text
security_privacy_and_ethics.md
```

---

# 73. Sensitive Data

Potentially sensitive data includes:

```text
source code
student notes
AI conversations
API metadata
device information
```

Never store secrets such as:

```text
API keys
passwords
tokens
```

inside learning records.

---

# 74. Data Encryption

Sensitive data should be encrypted:

```text
At Rest
In Transit
```

Especially:

```text
source code
AI conversations
authentication data
```

---

# 75. Database Relationships

High-level relationship graph:

```text
Student
 │
 ├── Sessions
 │      └── Events
 │
 ├── Skill States
 │      └── Mastery History
 │
 ├── Mistakes
 │      └── Mistake Patterns
 │
 ├── Behavior Observations
 │      └── Behavior Patterns
 │
 ├── Retrieval Attempts
 │      └── Retention State
 │
 └── Assessments
```

Problem relationships:

```text
Problem
 │
 ├── Skills
 ├── Test Cases
 ├── Difficulty
 ├── Learning Objectives
 └── Code Artifacts
```

---

# 76. Conceptual ER Model

```text
STUDENT
   │
   ├──────── SESSION
   │              │
   │              └──── EVENT
   │                     │
   │                     ├──── CODE ARTIFACT
   │                     ├──── EXECUTION
   │                     ├──── TEST EXECUTION
   │                     ├──── MISTAKE
   │                     └──── TUTOR INTERACTION
   │
   ├──────── STUDENT_SKILL_STATE
   │              │
   │              └──── MASTERY_SNAPSHOT
   │
   ├──────── BEHAVIOR_PATTERN
   │
   ├──────── RETENTION_STATE
   │
   └──────── ASSESSMENT

PROBLEM
   │
   ├──── PROBLEM_SKILL ──── SKILL
   │
   ├──── TEST_CASE
   │
   ├──── DIFFICULTY
   │
   └──── LEARNING_OBJECTIVE
```

---

# 77. Data Integrity Rules

Important rules:

```text
1. Every event belongs to a student.
2. Every session belongs to a student.
3. Every code artifact belongs to a problem/session where applicable.
4. Every mistake must reference evidence.
5. Every mastery state must identify its model version.
6. Every AI analysis must identify the model.
7. Derived states must never overwrite raw events.
8. Deleted data must respect privacy policies.
```

---

# 78. Temporal Consistency

Learning is temporal.

Therefore timestamps should be stored for:

```text
events
sessions
mistakes
mastery updates
retrieval
AI analysis
curriculum decisions
```

Do not rely only on:

```text
created_at
```

for learning logic.

---

# 79. Ordering

When analyzing behavior, CodeAtlas should use:

```text
event timestamp
```

rather than database insertion order.

This prevents incorrect conclusions from asynchronous processing.

---

# 80. Idempotency

Events may arrive more than once.

Every event should have a unique identifier.

If the same event arrives twice:

```text
Event ID
     ↓
Already processed?
     ├── YES → Ignore
     └── NO  → Process
```

---

# 81. Schema Versioning

Data schemas will evolve.

Every major event schema should contain:

```text
schema_version
```

Example:

```text
CODE_RUN
schema_version = 2
```

This enables future migrations.

---

# 82. Model Versioning

Similarly:

```text
mastery_model_version
mistake_model_version
difficulty_model_version
embedding_model_version
```

must be tracked.

---

# 83. Reproducibility

Given:

```text
Student
+
Events
+
Model Version
+
Configuration
```

CodeAtlas should ideally be able to reconstruct:

```text
Why did the system believe this?
```

---

# 84. Caching

Derived information can be cached.

Examples:

```text
current mastery
current student state
problem recommendations
embeddings
```

But caches should never become the only source of truth.

---

# 85. Analytics Warehouse

As CodeAtlas grows, analytical workloads should eventually be separated from transactional workloads.

Possible architecture:

```text
PostgreSQL
    ↓
Event Pipeline
    ↓
Analytics Store
```

This is not required for Version 1.

---

# 86. Version 1 Database

Keep the first implementation simple:

```text
PostgreSQL

Core tables:
students
sessions
events
problems
skills
problem_skills
code_artifacts
executions
test_cases
test_executions
mistakes
student_skill_states
hints
hint_requests
tutor_interactions
```

---

# 87. Version 2 Database

Add:

```text
evidence
mistake_patterns
behavior_observations
behavior_patterns
mastery_snapshots
retention_states
retrieval_attempts
curriculum_decisions
```

---

# 88. Version 3 Database

Add:

```text
experiments
experiment_assignments
metric_observations
decision_candidates
model_registry
embedding_store
```

---

# 89. Version 4

Potential infrastructure:

```text
event streaming
analytics warehouse
feature store
model registry
offline training pipeline
real-time inference pipeline
```

---

# 90. Data Flow Example

Student writes:

```python
while left < right:
    ...
```

CodeAtlas records:

```text
CODE_TYPED
```

Student runs code:

```text
CODE_RUN
```

Test fails:

```text
TEST_FAILED
```

AI/static analysis detects:

```text
OFF_BY_ONE
```

System creates:

```text
Evidence
```

Student skill state updates:

```text
Binary Search mastery
0.68 → 0.61
```

Adaptive engine decides:

```text
Target boundary handling
```

Problem selected:

```text
Novel binary-search problem
```

Later:

```text
Delayed retrieval succeeds
```

Mastery updates:

```text
0.61 → 0.73
```

This entire chain should remain traceable.

---

# 91. Example Event

Conceptual event:

```json
{
  "event_id": "evt_901",
  "student_id": "stu_001",
  "session_id": "ses_42",
  "event_type": "TEST_FAILED",
  "timestamp": "2026-08-23T18:42:10+05:30",
  "schema_version": 1,
  "payload": {
    "problem_id": "prob_102",
    "test_case_id": "test_7",
    "expected": 5,
    "actual": 6
  }
}
```

---

# 92. Derived Evidence Example

```json
{
  "evidence_id": "ev_721",
  "student_id": "stu_001",
  "source_event_id": "evt_901",
  "skill_id": "skill_binary_search_boundary",
  "evidence_type": "OFF_BY_ONE_FAILURE",
  "value": 1,
  "confidence": 0.93
}
```

---

# 93. Derived Student State Example

```json
{
  "student_id": "stu_001",
  "skill_id": "skill_binary_search_boundary",
  "mastery": 0.61,
  "confidence": 0.89,
  "retention": 0.54,
  "evidence_count": 17,
  "model_version": "mastery-v1.3",
  "updated_at": "2026-08-23T18:43:02+05:30"
}
```

---

# 94. Adaptive Decision Example

```json
{
  "decision_id": "dec_119",
  "student_id": "stu_001",
  "target_skill_id": "skill_binary_search_boundary",
  "selected_problem_id": "prob_208",
  "decision_type": "TARGETED_REMEDIATION",
  "reason": [
    "Repeated off-by-one errors",
    "Low retention",
    "Recent independent failure"
  ],
  "confidence": 0.87,
  "model_version": "adaptive-v1.0"
}
```

---

# 95. Data Model Design Rule

The most important rule is:

> **Do not store only what the system currently believes. Store enough evidence to reconstruct why it believes it.**

This is essential for:

```text
debugging
research
explainability
model improvement
privacy auditing
```

---

# 96. Final Architecture

```text
                    RAW DATA
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Events           Code         Tests
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                    EVIDENCE
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Mistakes         Behavior         Performance
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                 STUDENT MODEL
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Mastery     Retention    Behavior
          │            │            │
          └────────────┼────────────┘
                       ▼
                ADAPTIVE ENGINE
                       │
                       ▼
                 NEW ACTIVITY
                       │
                       ▼
                    EVENTS
```

---

# 97. Final Principle

CodeAtlas is not simply storing:

```text
"What did the student solve?"
```

It is building a longitudinal representation of:

```text
What the student attempted
What they thought
What they wrote
What failed
How they debugged
What help they needed
What they understood
What they forgot
What they transferred
What they repeatedly get wrong
How their behavior changes
```

That historical evidence is what allows CodeAtlas to evolve from:

```text
AI Coding Tutor
```

into:

```text
Personal Learning Intelligence System
```

# CodeAtlas — System Architecture

> **CodeAtlas is an adaptive personal coding intelligence system that observes how a programmer solves problems, builds a continuously evolving learner model, diagnoses weaknesses, and uses that model to adapt tutoring and practice.**

---

## 1. Architecture Vision

CodeAtlas is designed as a **closed-loop learning system**, not simply as an IDE with an AI chatbot attached.

The architecture is centered around the following loop:

```text
┌─────────────────────────────────────────────────────────────────┐
│                         CODEATLAS                               │
│                                                                 │
│   ┌──────────┐                                                  │
│   │ Student  │                                                  │
│   └────┬─────┘                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────────┐                                              │
│   │ Web IDE      │                                              │
│   └──────┬───────┘                                              │
│          │                                                      │
│          ▼                                                      │
│   ┌────────────────────┐                                        │
│   │ Observation Layer  │                                        │
│   └─────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│   ┌────────────────────┐                                        │
│   │ Analysis Layer     │                                        │
│   │                    │                                        │
│   │ Code Analysis      │                                        │
│   │ Error Analysis     │                                        │
│   │ Behavior Analysis  │                                        │
│   │ Mistake Detection  │                                        │
│   └─────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│   ┌────────────────────┐                                        │
│   │ Learner Model      │◄──────────── Historical Evidence       │
│   │                    │                                        │
│   │ Skills             │                                        │
│   │ Sub-skills         │                                        │
│   │ Mistakes           │                                        │
│   │ Behavior           │                                        │
│   │ Retention          │                                        │
│   │ Preferences        │                                        │
│   └─────────┬──────────┘                                        │
│             │                                                   │
│             ▼                                                   │
│   ┌────────────────────┐                                        │
│   │ Decision Layer      │                                        │
│   │                    │                                        │
│   │ Diagnosis          │                                        │
│   │ Curriculum         │                                        │
│   │ Intervention       │                                        │
│   │ Difficulty         │                                        │
│   └─────────┬──────────┘                                        │
│             │                                                   │
│       ┌─────┴─────────────┐                                     │
│       ▼                   ▼                                     │
│  ┌───────────┐      ┌──────────────┐                            │
│  │ AI Tutor  │      │ Problem      │                            │
│  │           │      │ Generator    │                            │
│  └─────┬─────┘      └──────┬───────┘                            │
│        │                    │                                    │
│        └─────────┬──────────┘                                    │
│                  ▼                                               │
│             ┌─────────┐                                         │
│             │ Student │                                         │
│             └─────────┘                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
````

The output of one learning session becomes evidence for the next.

---

# 2. Architectural Principles

CodeAtlas follows several architectural principles.

## 2.1 Learning System First

The IDE is an interface to the learning system.

The project should never evolve into:

```text
IDE + Chatbot
```

The central system is:

```text
Learner Model + Evidence + Adaptive Decisions
```

---

## 2.2 Evidence Before Inference

Raw observations should be stored separately from interpretations.

For example:

```text
Observation:
Student submitted code three times.

Inference:
Student may have difficulty debugging.

```

The second statement should not overwrite the first.

This distinction allows future algorithms to reinterpret historical evidence.

---

## 2.3 Event-Driven Learning

Important student actions should be represented as events.

Examples:

```text
CODE_EDITED
CODE_EXECUTED
TEST_CREATED
TEST_FAILED
TEST_PASSED
ERROR_OCCURRED
HINT_REQUESTED
QUESTION_ASKED
SOLUTION_VIEWED
PROBLEM_STARTED
PROBLEM_COMPLETED
PROBLEM_ABANDONED
ALGORITHM_CHANGED
SESSION_ENDED
```

Events provide the raw material for behavioral analysis.

---

## 2.4 Model State Separately From Events

Events describe:

> What happened?

The learner model describes:

> What do we currently believe about the learner?

Example:

```text
Event:
OFF_BY_ONE_ERROR

↓

Evidence accumulation

↓

Learner Model:
Boundary Handling
mastery = 0.42
confidence = 0.81
```

The learner model should be derived from evidence rather than becoming an opaque collection of manually modified values.

---

## 2.5 AI Is a Component, Not the Architecture

LLMs are powerful but should not own the entire system.

CodeAtlas separates:

```text
Deterministic Systems
        +
Statistical / ML Systems
        +
LLM Systems
```

This improves:

* reproducibility
* observability
* testability
* cost control
* model independence
* reliability

---

# 3. High-Level Architecture

```text
                           ┌──────────────────┐
                           │      Student     │
                           └────────┬─────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      Web Client      │
                         │                      │
                         │ IDE                  │
                         │ Dashboard            │
                         │ Tutor                │
                         │ Practice              │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      API Layer       │
                         └──────────┬───────────┘
                                    │
             ┌──────────────────────┼──────────────────────┐
             │                      │                      │
             ▼                      ▼                      ▼
      ┌────────────┐        ┌─────────────┐       ┌──────────────┐
      │ Session    │        │ Code        │       │ Learning     │
      │ Service    │        │ Execution   │       │ Service      │
      └─────┬──────┘        └──────┬──────┘       └──────┬───────┘
            │                      │                     │
            └──────────────┬───────┴─────────────────────┘
                           ▼
                  ┌────────────────────┐
                  │ Event / Observation│
                  │ Pipeline           │
                  └─────────┬──────────┘
                            │
            ┌───────────────┼────────────────┐
            ▼               ▼                ▼
     ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
     │ Code        │ │ Behavior    │ │ Mistake      │
     │ Analysis    │ │ Analysis    │ │ Detection    │
     └──────┬──────┘ └──────┬──────┘ └──────┬───────┘
            │               │                │
            └───────────────┼────────────────┘
                            ▼
                   ┌──────────────────┐
                   │ Evidence Store   │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Learner Model    │
                   └────────┬─────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │ Adaptive Decision   │
                  │ Engine              │
                  └──────────┬──────────┘
                             │
               ┌─────────────┼──────────────┐
               ▼             ▼              ▼
        ┌────────────┐ ┌───────────┐ ┌────────────┐
        │ Curriculum │ │ Tutor     │ │ Problem    │
        │ Engine     │ │ Engine    │ │ Generator  │
        └─────┬──────┘ └─────┬─────┘ └──────┬─────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                        Student
```

---

# 4. Major Architectural Layers

CodeAtlas is divided into seven logical layers.

```text
1. Experience Layer
2. Application Layer
3. Execution Layer
4. Observation Layer
5. Intelligence Layer
6. Data Layer
7. Infrastructure Layer
```

---

# 5. Experience Layer

The experience layer contains everything the student directly interacts with.

## Components

### Web IDE

Responsibilities:

* Code editing
* File management
* Language selection
* Code execution
* Test creation
* Test execution
* Debugging interface
* Submission

---

### AI Tutor Interface

Provides:

* conversational tutoring
* hints
* explanations
* Socratic questioning
* debugging guidance
* concept explanations
* reflection prompts

The tutor interface should not directly decide what the student needs.

It receives decisions from the tutoring engine.

---

### Learning Dashboard

Displays:

* skill progression
* current weaknesses
* recent mistakes
* learning streak
* retention alerts
* recommended practice
* learning trends

The dashboard should avoid presenting uncertain model predictions as absolute facts.

For example:

```text
Bad:
"You are bad at recursion."

Better:
"Recent evidence suggests recursion may be an area to reinforce."
```

---

# 6. Application Layer

The application layer coordinates user-facing operations.

Major services include:

```text
Authentication Service
Session Service
Problem Service
Submission Service
Tutor Service
Practice Service
Learning Service
Analytics Service
```

These services should remain independent from the underlying AI provider.

---

# 7. Code Execution Layer

CodeAtlas must execute user code safely.

The execution architecture should eventually resemble:

```text
Student Code
     │
     ▼
Execution Request
     │
     ▼
Sandbox Manager
     │
     ▼
Isolated Runtime
     │
     ├── CPU Limit
     ├── Memory Limit
     ├── Time Limit
     ├── Process Limit
     ├── Network Isolation
     └── Filesystem Isolation
     │
     ▼
Execution Result
     │
     ├── stdout
     ├── stderr
     ├── exit code
     ├── runtime
     ├── memory
     └── status
```

Code execution must be treated as a security boundary.

The web application must never execute arbitrary student code directly on the application server.

---

# 8. Observation Layer

The observation layer converts activity into structured events.

Example:

```text
Student types code
        ↓
CODE_EDITED
        ↓
Student executes code
        ↓
CODE_EXECUTED
        ↓
Runtime error
        ↓
ERROR_OCCURRED
        ↓
Student modifies code
        ↓
CODE_EDITED
        ↓
Student executes again
        ↓
TEST_FAILED
```

The observation layer should capture both:

### Explicit events

Actions directly performed by the student.

### Derived events

Events inferred from activity.

Example:

```text
5 rapid code revisions
+
same failing test
+
no new test
=
POSSIBLE_UNSYSTEMATIC_DEBUGGING
```

Derived events must maintain a confidence score.

---

# 9. Code Analysis Layer

The code analysis subsystem analyzes source code independently of the LLM where possible.

Potential capabilities include:

```text
Syntax analysis
AST analysis
Complexity analysis
Code structure analysis
Pattern detection
Static analysis
Test analysis
Dependency analysis
```

For supported languages, AST-based analysis should be preferred over raw text analysis.

Example:

```text
Source Code
    ↓
Parser
    ↓
AST
    ↓
Structural Analysis
    ↓
Features
```

These features become evidence for the learner model.

---

# 10. Behavior Analysis Layer

Behavior analysis studies the student's interaction with the environment.

Potential signals:

```text
Time to first attempt
Time between edits
Number of revisions
Number of executions
Hint frequency
Question frequency
Test creation behavior
Debugging order
Algorithm switching
Solution viewing
Abandonment
```

Example:

```text
Execution failed
      ↓
Student immediately requests hint
      ↓
Hint given
      ↓
Student copies suggested implementation
      ↓
Solution succeeds
```

This should potentially generate:

```text
Possible:
high assistance dependency
```

It should **not automatically become**:

```text
Student cannot solve problems independently
```

The learner model must aggregate evidence over time.

---

# 11. Mistake Detection Layer

Mistake detection combines:

```text
Execution Results
+
Code Analysis
+
Problem Metadata
+
Behavior
+
LLM Reasoning
```

Example:

```text
Expected:
O(n)

Student:
O(n²)

        ↓

Complexity Analysis

        ↓

COMPLEXITY_MISTAKE
```

Another example:

```text
Problem requires:
sorted array

Student uses:
hash map

Correctness:
works

Complexity:
acceptable

        ↓

No mistake
```

The system should avoid labeling stylistic differences as mistakes.

---

# 12. Evidence Layer

The evidence layer is one of the most important architectural components.

It stores observations that can later influence the learner model.

Example:

```text
Evidence
├── source
├── event
├── skill
├── subskill
├── timestamp
├── confidence
├── context
└── strength
```

Example:

```text
Evidence:

student_id:
001

event:
OFF_BY_ONE_ERROR

skill:
Binary Search

subskill:
Boundary Handling

confidence:
0.91

timestamp:
2026-08-23

source:
Static Analyzer + Test Failure
```

Evidence should be immutable whenever possible.

---

# 13. Learner Model

The learner model represents the system's current belief about the student.

Conceptually:

```text
Learner Model
│
├── Skill State
│
├── Mistake State
│
├── Behavioral State
│
├── Retention State
│
├── Intervention Preferences
│
└── Learning History
```

A skill state might contain:

```text
mastery
confidence
evidence_count
last_success
last_failure
difficulty_history
retention_estimate
trend
```

Important:

> Mastery and confidence are different.

Example:

```text
mastery = 0.72
confidence = 0.31
```

could mean:

> The evidence suggests moderate skill, but there is not enough evidence to be highly confident.

---

# 14. Skill Graph

CodeAtlas should eventually represent programming knowledge as a graph.

Example:

```text
Arrays
  │
  ├── Prefix Sum
  │
  └── Two Pointer
          │
          ▼
     Sliding Window

Recursion
   │
   ▼
Tree Traversal
   │
   ▼
DFS
   │
   ▼
Graph Algorithms
```

Edges may represent:

```text
PREREQUISITE
RELATED_TO
EXTENDS
GENERALIZES
SPECIALIZES
```

This allows the system to reason about root causes.

For example:

```text
Weak Graph DFS
       ↓
Check DFS subskills
       ↓
Recursion weak
       ↓
Recommendation:
reinforce recursion
```

---

# 15. Adaptive Decision Layer

The decision layer converts learner state into actions.

It contains:

```text
Diagnosis Engine
Difficulty Engine
Curriculum Engine
Intervention Selector
Retention Scheduler
Problem Selector
```

The central decision process is:

```text
Current learner state
        +
Current problem state
        +
Historical evidence
        +
Learning objective
        ↓
Adaptive Decision
```

---

# 16. Curriculum Engine

The curriculum engine determines:

> What should the student practice next?

Initial curriculum policy:

```text
40% Current weaknesses
30% New learning
20% Forgotten concepts
10% Mastered concepts
```

This should eventually become adaptive.

Potential future formulation:

```text
Expected Learning Gain
----------------------
Expected Cost
```

The engine should prioritize interventions that are likely to provide high learning value.

---

# 17. Tutoring Engine

The tutoring engine determines how the AI should interact with the student.

Possible modes:

```text
HINT
SOCRATIC_QUESTION
DIAGNOSTIC_QUESTION
CONCEPT_EXPLANATION
DEBUGGING_GUIDANCE
WORKED_EXAMPLE
REFLECTION
CHALLENGE
```

The tutoring engine should consider:

```text
Current mistake
+
Student skill
+
Previous interventions
+
Hint dependency
+
Problem difficulty
+
Learning objective
```

Then select an intervention.

---

# 18. Problem Generator

The problem generator creates or selects programming tasks.

Every problem should have structured metadata.

```text
Problem
├── topic
├── subskills
├── prerequisites
├── difficulty
├── learning_objective
├── expected_complexity
├── common_mistakes
├── constraints
└── test_strategy
```

The generator should support:

```text
New problems
Problem variants
Skill-targeted problems
Mistake-targeted problems
Transfer problems
Retention problems
Challenge problems
```

---

# 19. AI Gateway

CodeAtlas should use an abstraction layer between the application and AI providers.

```text
                  ┌───────────────┐
                  │ CodeAtlas AI  │
                  │ Gateway       │
                  └───────┬───────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Gemini        Groq       Local Model
```

The rest of the system should not directly depend on:

```text
Gemini API
Groq API
OpenAI API
```

Instead:

```text
TutorEngine
     ↓
AI Gateway
     ↓
Provider Adapter
     ↓
LLM
```

This makes providers replaceable.

---

# 20. AI Request Pipeline

An AI request should generally follow:

```text
User Request
      ↓
Context Builder
      ↓
Relevant Learner State
      ↓
Problem Context
      ↓
Recent Evidence
      ↓
Tutor Policy
      ↓
Prompt Construction
      ↓
AI Gateway
      ↓
LLM
      ↓
Response Validation
      ↓
Tutor Response
```

The context builder should avoid blindly sending the entire learner history to the LLM.

Only relevant context should be selected.

---

# 21. Data Architecture

At a conceptual level:

```text
┌─────────────────────────────┐
│ Transactional Database      │
│                             │
│ Users                       │
│ Problems                    │
│ Sessions                    │
│ Attempts                    │
│ Skills                      │
│ Learner State               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Event Store                 │
│                             │
│ Coding Events               │
│ Interaction Events          │
│ Learning Events             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Analytics / Feature Store   │
│                             │
│ Behavioral Features         │
│ Learning Features           │
│ Historical Aggregations     │
└─────────────────────────────┘
```

The first implementation does not need a distributed data architecture.

The architecture should evolve only when scale or research requirements justify it.

---

# 22. Event Flow

A typical coding session:

```text
Student opens problem
        │
        ▼
PROBLEM_STARTED
        │
        ▼
Student writes code
        │
        ▼
CODE_EDITED
        │
        ▼
Student executes
        │
        ▼
CODE_EXECUTED
        │
        ├───────────────┐
        ▼               ▼
Success              Failure
                        │
                        ▼
                 ERROR_OCCURRED
                        │
                        ▼
                 Mistake Detector
                        │
                        ▼
                 Evidence Created
                        │
                        ▼
                 Learner Model Update
                        │
                        ▼
                 Tutor Decision
                        │
                        ▼
                   Intervention
                        │
                        ▼
                  Student retries
```

---

# 23. Session Lifecycle

```text
START_SESSION
      ↓
LOAD_LEARNER_CONTEXT
      ↓
SELECT_OR_OPEN_PROBLEM
      ↓
OBSERVE_ACTIVITY
      ↓
ANALYZE_ACTIVITY
      ↓
UPDATE_EVIDENCE
      ↓
UPDATE_LEARNER_MODEL
      ↓
ADAPT_IF_NEEDED
      ↓
PROBLEM_COMPLETED
      ↓
EVALUATE
      ↓
STORE_SESSION_SUMMARY
      ↓
UPDATE_CURRICULUM
      ↓
END_SESSION
```

---

# 24. Separation of Concerns

The architecture must prevent the following anti-pattern:

```text
Frontend
   ↓
LLM
   ↓
Database
```

Instead:

```text
Frontend
   ↓
API
   ↓
Application Services
   ↓
Domain / Intelligence Layer
   ↓
Persistence
```

For example:

```text
Frontend
   ↓
POST /tutor/hint
   ↓
Tutor Service
   ↓
Tutor Engine
   ↓
Learner Model
   ↓
Intervention Selector
   ↓
Context Builder
   ↓
AI Gateway
   ↓
LLM
```

---

# 25. Domain Boundaries

The major domain boundaries are:

```text
Identity
Learning
Coding
Execution
Tutoring
Curriculum
Problems
Analytics
AI
```

A future service architecture may separate these domains physically.

Initially, they can exist as modules within a modular monolith.

---

# 26. Initial Architecture Strategy

The first implementation should **not** begin with microservices.

Recommended initial architecture:

```text
                 CodeAtlas
                    │
        ┌───────────┴───────────┐
        │                       │
    Frontend                 Backend
        │                       │
        │              ┌────────┴────────┐
        │              │                 │
        │          Application       Intelligence
        │              │                 │
        │              │                 │
        │          Domain Layer     AI/ML Layer
        │              │                 │
        │              └────────┬────────┘
        │                       │
        │                  Persistence
        │                       │
        └───────────────────────┘
```

This should be a **modular monolith** initially.

The modules must have clear boundaries so that they can later be extracted into services if necessary.

---

# 27. Why Modular Monolith First?

The system has many interacting domains.

Premature microservices would introduce:

* network complexity
* distributed debugging
* deployment complexity
* synchronization problems
* authentication complexity
* observability overhead

before the learning architecture itself is validated.

The first objective is to validate:

> **Does the learning loop actually work?**

not:

> **Can we operate 25 distributed services?**

---

# 28. Future Evolution

The architecture may evolve toward:

```text
                    API Gateway
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
 Coding Service    Learning Service   Tutor Service
       │                 │                 │
       ▼                 ▼                 ▼
 Execution          Learner Model      AI Gateway
 Service                 │                 │
                         ▼                 ▼
                    ML Services       LLM Providers
```

This transition should happen only when justified by:

* scale
* isolation
* performance
* independent deployment
* research workloads
* security requirements

---

# 29. Observability

Every important system action should be observable.

We need:

```text
Application Logs
Structured Events
Metrics
Error Tracking
AI Request Logs
Learning Decisions
Model Updates
```

For adaptive decisions, the system should ideally be able to answer:

> Why was this problem recommended?

Example:

```text
Recommendation:

Problem: Binary Search Variant #17

Reasons:
- Boundary Handling mastery: 0.43
- 3 recent boundary errors
- Last practice: 9 days ago
- Transfer score: low
- Difficulty: moderate
```

This is critical for debugging the learning system itself.

---

# 30. Explainability of Decisions

Adaptive decisions should be traceable.

Instead of:

```text
Next Problem:
Graph Problem 42
```

the system should internally produce something similar to:

```text
Decision:

Target skill:
DFS traversal

Evidence:
- 4 recent DFS errors
- 2 incorrect recursion base cases
- last successful DFS problem: 12 days ago

Reason:
High estimated weakness + retention risk

Selected intervention:
Guided DFS problem

Confidence:
0.78
```

The user-facing representation can be simplified.

---

# 31. Reliability Boundaries

AI-generated information should not automatically become authoritative learner state.

For example:

```text
LLM:
"Student probably doesn't understand recursion."
```

should become:

```text
Hypothesis
confidence = 0.42
```

not:

```text
recursion_mastery = 0.10
```

The learner model should require evidence accumulation.

---

# 32. Security Boundaries

The architecture contains several high-risk boundaries:

```text
Student Code
      ↓
Code Execution Sandbox

Student Input
      ↓
LLM Context

External AI Provider
      ↓
Student Data

Browser
      ↓
Backend API
```

Each boundary must have explicit security controls.

Detailed security requirements are defined in:

```text
docs/security_privacy_and_ethics.md
```

---

# 33. Architectural Data Flow

The overall intelligence pipeline is:

```text
               RAW ACTIVITY
                    │
                    ▼
              OBSERVATIONS
                    │
                    ▼
                 EVENTS
                    │
                    ▼
                FEATURES
                    │
                    ▼
                EVIDENCE
                    │
                    ▼
             LEARNER MODEL
                    │
                    ▼
              DIAGNOSIS
                    │
                    ▼
           ADAPTIVE DECISION
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Problem    Tutor    Review
       Selection  Mode     Schedule
          │         │         │
          └─────────┼─────────┘
                    ▼
                STUDENT
                    │
                    ▼
              NEW EVIDENCE
```

This is the central intelligence loop of CodeAtlas.

---

# 34. Architectural Invariants

The following rules should remain true unless the architecture is intentionally redesigned.

### Invariant 1

Raw observations must remain distinguishable from inferred learner state.

### Invariant 2

The learner model must be evidence-driven.

### Invariant 3

The frontend must not directly depend on a specific LLM provider.

### Invariant 4

Arbitrary code must never execute inside the application server.

### Invariant 5

Adaptive decisions must be traceable.

### Invariant 6

AI-generated diagnoses must carry uncertainty.

### Invariant 7

The system must support replacing AI providers.

### Invariant 8

Learning state must persist across sessions.

### Invariant 9

The system must support unfamiliar-problem evaluation.

### Invariant 10

The architecture must allow the learner model to become more sophisticated without requiring a complete rewrite.

---

# 35. Architecture Evolution

CodeAtlas should evolve through architectural maturity levels.

## Level 1 — Functional Prototype

```text
Web IDE
+
Backend
+
Database
+
LLM API
```

---

## Level 2 — Learning-Aware System

```text
Event Tracking
+
Mistake Detection
+
Skill Tracking
+
Basic Learner Model
```

---

## Level 3 — Adaptive System

```text
Learner Model
+
Adaptive Curriculum
+
Adaptive Tutoring
+
Retention
```

---

## Level 4 — Intelligent Learning System

```text
ML Skill Estimation
+
Behavior Modeling
+
Intervention Optimization
+
Transfer Evaluation
```

---

## Level 5 — Personal Coding Intelligence

```text
Longitudinal Learner Model
+
Knowledge Graph
+
Adaptive Policies
+
Personalized Learning Science
+
Research-grade Evaluation
```

The project should be allowed to reach Level 5 without requiring the early architecture to be discarded.

---

# 36. Architectural Goal

The ultimate architecture should enable CodeAtlas to answer:

```text
What did the student do?
        ↓
What happened?
        ↓
What mistake occurred?
        ↓
Why might it have happened?
        ↓
What does this tell us about the learner?
        ↓
What does the learner need next?
        ↓
What intervention should we use?
        ↓
Did the intervention work?
        ↓
What should we change about our belief?
```

That loop is the actual intelligence of CodeAtlas.

The IDE, LLM, database and ML models are supporting infrastructure around it.

---

# 37. Related Documents

This document defines the system-level architecture.

Detailed responsibilities are defined in:

* `VISION.md` — Project vision and principles
* `Problem_Statement.md` — Problem being solved
* `PRD.md` — Product requirements
* `Learning_model.md` — Learner representation
* `mistake_taxonomy.md` — Mistake classification
* `behavior_model.md` — Behavioral representation
* `Adaptive_curriculum.md` — Curriculum adaptation
* `tutoring_engine.md` — Adaptive tutoring
* `forgetting_and_retention.md` — Retention and forgetting
* `problem_generator.md` — Problem generation
* `ai_and_ml_strategy.md` — AI/ML strategy
* `evaluation_framework.md` — Evaluation methodology
* `data_model.md` — Persistence and data structures
* `security_privacy_and_ethics.md` — Security and privacy
* `ROADMAP.md` — Architecture evolution
* `DESIGN.md` — Cross-cutting engineering decisions

---

# 38. Final Architectural Principle

> **CodeAtlas should be architected as a learning intelligence system that happens to contain an IDE, not as an IDE that happens to contain AI.**

The distinction is fundamental.

The IDE produces observations.

The intelligence layer interprets those observations.

The learner model accumulates knowledge.

The adaptive system decides what happens next.

The student provides new evidence.

And the cycle continues.


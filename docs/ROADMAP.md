# CodeAtlas — Roadmap

> **Version:** 0.1  
> **Status:** Strategic Development Roadmap  
> **Project:** CodeAtlas  
> **Target:** Research-grade Personal Coding Intelligence System  
> **Development Philosophy:** Build the learning intelligence first, then scale the platform around it.

---

# 1. Vision

CodeAtlas should evolve through the following progression:

```text
Web-based Coding IDE
        ↓
Coding Activity Tracker
        ↓
Mistake Detection System
        ↓
Student Skill Model
        ↓
Behavior Model
        ↓
Adaptive Tutor
        ↓
Adaptive Curriculum
        ↓
Long-term Retention System
        ↓
Personal Coding Intelligence
        ↓
Research-grade Learning Agent
````

The goal is **not** to build another AI coding assistant.

The goal is to build a system that can answer:

> "What does this student currently understand, what are they getting wrong, why are they getting it wrong, what are they likely to forget, and what should they practice next?"

---

# 2. Development Philosophy

CodeAtlas should not be developed as:

```text
Frontend
→ Backend
→ AI API
→ Done
```

Instead:

```text
Evidence
→ Models
→ Intelligence
→ Adaptive Decisions
→ User Experience
```

The intelligence must drive the product.

---

# 3. Project Levels

The project is divided into four major levels.

```text
Level 1 — Foundation
Level 2 — Personalization
Level 3 — Adaptive Intelligence
Level 4 — Research-Grade System
```

---

# 4. Level 1 — Foundation

## Objective

Build a reliable coding environment capable of collecting high-quality behavioral evidence.

The system should already be useful without sophisticated AI.

---

## Phase 1.1 — Repository & Engineering Foundation

### Goals

Create the engineering foundation.

### Tasks

* Initialize repository
* Define branch strategy
* Configure linting
* Configure formatting
* Configure testing
* Configure environment management
* Configure CI
* Configure pre-commit checks
* Establish documentation structure
* Define coding standards

### Deliverables

```text
Repository
CI pipeline
Development environment
Testing infrastructure
Documentation system
```

---

# 5. Phase 1.2 — Application Skeleton

Build the initial application:

```text
Frontend
    ↓
Backend API
    ↓
Database
```

### Initial functionality

* Authentication
* Dashboard
* Problem browser
* Problem page
* Code editor
* Code execution
* Test execution
* Submission

---

# 6. Phase 1.3 — Code Execution Engine

Build secure execution infrastructure.

### Support initially

Choose a limited set of languages.

Recommended:

```text
Python
C++
```

Potential later:

```text
Java
JavaScript
C
Go
Rust
```

### Requirements

* Sandbox
* CPU limits
* Memory limits
* Timeout
* Process limits
* Output limits
* Network isolation

---

# 7. Phase 1.4 — Event Tracking

Implement the event system.

Track:

```text
Code typed
Code saved
Code run
Test created
Test executed
Test failed
Test passed
Hint requested
Code revised
Problem completed
Problem abandoned
```

---

# 8. Phase 1.5 — Code Versioning

Track code revisions.

Implement:

```text
Code Artifact
      ↓
Parent Artifact
      ↓
Diff
```

This allows CodeAtlas to understand:

```text
How the student reached the final solution.
```

---

# 9. Phase 1.6 — Basic Analytics

Build the first student dashboard.

Display:

```text
Problems solved
Average solve time
Attempts/problem
Tests written
Hints requested
Languages used
Recent mistakes
```

At this stage:

> **Do not pretend that these statistics are intelligence.**

They are observations.

---

# 10. Level 1 Exit Criteria

Level 1 is complete when CodeAtlas can reliably answer:

```text
What did the student do?
When did they do it?
What code did they write?
What happened when they ran it?
How did their code evolve?
```

---

# 11. Level 2 — Personalization

## Objective

Turn raw coding activity into a representation of the student.

---

# 12. Phase 2.1 — Skill Taxonomy

Create the programming skill graph.

Example:

```text
Programming
├── Syntax
├── Data Structures
├── Algorithms
├── Problem Solving
├── Debugging
├── Complexity
└── Software Engineering
```

Then expand into subskills.

Example:

```text
Algorithms
└── Searching
    └── Binary Search
        ├── Search Space
        ├── Invariants
        ├── Boundaries
        └── Complexity
```

---

# 13. Phase 2.2 — Mistake Detection

Implement the first mistake classifier.

Categories:

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

# 14. Detection Strategy

Do not immediately rely entirely on an LLM.

Use:

```text
Compiler
+
AST
+
Runtime
+
Tests
+
Static Analysis
+
Code Diff
+
LLM
```

The system should combine evidence.

---

# 15. Phase 2.3 — Mistake Evidence

For every detected mistake:

```text
Mistake
    ↓
Evidence
    ↓
Confidence
    ↓
Skill relationship
```

Example:

```text
Off-by-one
Confidence: 0.93

Evidence:
Loop accesses index n
while valid indices are 0...n-1
```

---

# 16. Phase 2.4 — Student Skill Model

Implement:

```text
Student
   ↓
Skill
   ↓
Mastery
   ↓
Confidence
   ↓
Evidence Count
```

Initially use a simple probabilistic model.

Avoid jumping immediately into complex deep learning.

---

# 17. Phase 2.5 — Behavior Model

Track behavioral patterns.

Examples:

```text
Rushing
Overengineering
Low testing
Hint dependency
Random editing
Premature solution reveal
Persistence
Abandonment
```

---

# 18. Phase 2.6 — First Personalized Dashboard

The dashboard should evolve from:

```text
You solved 42 problems.
```

to:

```text
Your strongest skills:
Hash Maps
Binary Search

Skills needing attention:
Recursion State
Boundary Conditions

Behavior:
You tend to write code before testing your assumptions.

Recent pattern:
3 consecutive boundary-related mistakes.
```

---

# 19. Level 2 Exit Criteria

CodeAtlas should now answer:

```text
What does this student know?
What are they weak at?
What mistakes do they repeat?
How do they behave while solving?
```

---

# 20. Level 3 — Adaptive Intelligence

## Objective

Make CodeAtlas decide what the student should do next.

---

# 21. Phase 3.1 — Tutoring Engine

Implement the tutoring loop:

```text
Student
   ↓
Attempt
   ↓
Observe
   ↓
Diagnose
   ↓
Hint
   ↓
Observe Again
   ↓
Adapt
```

---

# 22. Hint Ladder

Implement graduated assistance.

```text
Level 0
No help

Level 1
Question

Level 2
Concept reminder

Level 3
Strategic hint

Level 4
Detailed guidance

Level 5
Partial pseudocode

Level 6
Solution explanation
```

The system should prefer the smallest useful intervention.

---

# 23. Phase 3.2 — Problem Generator

Build a problem generation system.

It should generate problems based on:

```text
Skill
Subskill
Difficulty
Mistake history
Behavior
Retention
Language
Recent performance
```

---

# 24. Generated Problem Validation

Generated problems must be validated.

Pipeline:

```text
Generate
   ↓
Syntax Validation
   ↓
Test Generation
   ↓
Solution Verification
   ↓
Difficulty Evaluation
   ↓
Duplicate Detection
   ↓
Quality Check
   ↓
Publish
```

---

# 25. Phase 3.3 — Adaptive Difficulty

Implement difficulty adjustment.

The system should estimate:

```text
Expected Success
Expected Learning Gain
```

Then select an appropriate challenge.

Avoid:

```text
Always easier
```

and:

```text
Always harder
```

---

# 26. Phase 3.4 — Adaptive Curriculum

Instead of random problem selection:

```text
Problem A
Problem B
Problem C
```

use:

```text
Student State
     ↓
Skill Gap
     ↓
Prerequisites
     ↓
Retention
     ↓
Problem Selection
```

---

# 27. Phase 3.5 — Retrieval Practice

Introduce deliberate retrieval.

Example:

```text
Day 1
Learn Binary Search

Day 2
Practice variation

Day 5
Retrieve without hints

Day 12
Novel problem

Day 30
Transfer problem
```

---

# 28. Phase 3.6 — Forgetting Model

Track:

```text
Mastery
Retention
Time Since Practice
Retrieval Success
Retrieval Failure
```

Then estimate:

```text
P(skill retained)
```

---

# 29. Phase 3.7 — Transfer Learning

This is a major milestone.

CodeAtlas should distinguish:

```text
Can solve familiar problem
```

from:

```text
Can recognize and apply concept in unfamiliar problem
```

Example:

A student solves:

```text
Binary Search in sorted array
```

Then CodeAtlas tests:

```text
Binary Search on answer space
```

Success indicates stronger conceptual understanding.

---

# 30. Level 3 Exit Criteria

CodeAtlas should be able to answer:

```text
What should this student practice next?
Why?
At what difficulty?
How much assistance should be given?
When should the concept be revisited?
```

---

# 31. Level 4 — Research-Grade CodeAtlas

## Objective

Move from an advanced product into an experimental learning intelligence platform.

---

# 32. Phase 4.1 — Unified Student Model

Combine:

```text
Knowledge
+
Mistakes
+
Behavior
+
Retention
+
Performance
+
Preferences
```

into a unified student state.

Conceptually:

```text
Student State
{
    knowledge,
    misconceptions,
    behavior,
    retention,
    preferences,
    confidence,
    learning_velocity
}
```

---

# 33. Phase 4.2 — Temporal Student Modeling

Instead of:

```text
Current mastery
```

model:

```text
Mastery(t)
```

This allows CodeAtlas to understand:

```text
learning
forgetting
relearning
plateaus
regression
transfer
```

---

# 34. Phase 4.3 — Causal Learning Experiments

Move beyond correlation.

Example hypothesis:

```text
Does weaker hinting improve independent problem solving?
```

Experiment:

```text
Group A
Full explanations

Group B
Progressive hints
```

Measure:

```text
Immediate success
Delayed retention
Transfer
Hint dependency
```

---

# 35. Phase 4.4 — Recommendation Engine

Treat problem selection as a sequential decision problem.

Potential approaches:

```text
Contextual Bandits
Reinforcement Learning
Bayesian Optimization
Knowledge Tracing
```

The goal:

```text
Choose activity
→ observe result
→ update student model
→ choose next activity
```

---

# 36. Phase 4.5 — Personalized Learning Policy

Eventually CodeAtlas should learn:

```text
For this student,
under these conditions,
this type of intervention
usually produces the highest learning gain.
```

This is significantly beyond conventional recommendation systems.

---

# 37. Phase 4.6 — Meta-Learning

Study:

```text
How does the student learn?
```

rather than only:

```text
What does the student know?
```

Potential features:

```text
Hint responsiveness
Error correction speed
Concept transfer speed
Retrieval decay
Learning velocity
Preferred explanation style
```

---

# 38. Phase 4.7 — Self-Evaluation

CodeAtlas should evaluate its own recommendations.

For every decision:

```text
Recommendation
      ↓
Outcome
      ↓
Expected vs Actual
      ↓
Policy Evaluation
```

---

# 39. Phase 4.8 — Model Calibration

If CodeAtlas predicts:

```text
85% chance of success
```

then across many predictions approximately:

```text
85% should succeed
```

if the model is calibrated.

Track:

```text
Calibration
Confidence
Prediction Error
```

---

# 40. Phase 4.9 — Counterfactual Evaluation

Ask:

> What would have happened if we had chosen a different problem?

Example:

```text
Selected:
Medium recursion problem

Alternative:
Retrieval problem

Observed outcome:
Student failed

Counterfactual:
Would retrieval have produced more learning?
```

This is a difficult but valuable research direction.

---

# 41. Phase 4.10 — Research Benchmark

Create a benchmark specifically for CodeAtlas.

Measure:

```text
Mastery prediction
Mistake classification
Difficulty estimation
Recommendation quality
Retention prediction
Transfer prediction
Hint effectiveness
Learning gain
```

---

# 42. Core Evaluation Metrics

CodeAtlas should eventually measure:

### Learning

```text
Mastery Gain
Retention
Transfer
Independent Success
```

### Tutor Quality

```text
Hint Effectiveness
Hint Dependency
Explanation Quality
Diagnosis Accuracy
```

### Adaptation

```text
Recommendation Accuracy
Difficulty Calibration
Curriculum Efficiency
```

### System

```text
Latency
Cost
Reliability
Sandbox Security
```

---

# 43. Anti-Metric

CodeAtlas should explicitly avoid optimizing solely for:

```text
Problems Solved
Sessions
Time Spent
AI Messages
```

These are engagement metrics, not learning metrics.

---

# 44. Milestone Matrix

| Milestone | Capability                     |
| --------- | ------------------------------ |
| M1        | Working coding IDE             |
| M2        | Secure execution               |
| M3        | Event tracking                 |
| M4        | Code version history           |
| M5        | Mistake detection              |
| M6        | Skill model                    |
| M7        | Behavior model                 |
| M8        | Personalized dashboard         |
| M9        | Tutor engine                   |
| M10       | Problem generation             |
| M11       | Adaptive difficulty            |
| M12       | Adaptive curriculum            |
| M13       | Retrieval system               |
| M14       | Retention model                |
| M15       | Transfer evaluation            |
| M16       | Learning policy                |
| M17       | Research benchmark             |
| M18       | Self-evaluating learning agent |

---

# 45. Suggested Implementation Order

The recommended order is:

```text
1. Repository
2. Backend
3. Database
4. Authentication
5. IDE
6. Code execution
7. Event system
8. Code versioning
9. Basic analytics
10. Skill taxonomy
11. Mistake taxonomy
12. Mistake detection
13. Student skill model
14. Behavior model
15. Tutor engine
16. Problem generator
17. Adaptive difficulty
18. Adaptive curriculum
19. Retrieval
20. Retention model
21. Transfer evaluation
22. Recommendation engine
23. Research infrastructure
```

---

# 46. What NOT To Build Early

Avoid prematurely building:

```text
❌ Reinforcement learning
❌ Complex neural student model
❌ Fine-tuned LLM
❌ Multi-agent architecture
❌ Huge vector database
❌ 20-language execution
❌ Mobile application
❌ Social features
❌ Gamification system
```

The first objective is to collect **high-quality evidence**.

---

# 47. Why This Order Matters

Suppose we build an RL recommendation engine before collecting useful student data.

We get:

```text
Sophisticated algorithm
+
Poor observations
=
Sophisticated nonsense
```

CodeAtlas should instead follow:

```text
Reliable evidence
        ↓
Reliable representation
        ↓
Reliable diagnosis
        ↓
Reliable adaptation
        ↓
Advanced learning algorithms
```

---

# 48. Technical Evolution

## Stage 1

```text
Next.js / React
FastAPI
PostgreSQL
Docker
```

---

## Stage 2

Add:

```text
Redis
Background workers
Object storage
LLM gateway
```

---

## Stage 3

Add:

```text
Event processing
Feature computation
Vector search
Model inference services
```

---


Do not introduce distributed infrastructure before the system actually needs it.

---

# 49. AI Evolution

AI should evolve in stages.

### Stage 1

```text
External LLM API
```

Use for:

```text
explanations
hints
mistake reasoning
problem generation
```

---

### Stage 2

Add deterministic intelligence:

```text
AST
Static analysis
Complexity analysis
Test analysis
Code diff analysis
```

---

### Stage 3

Add specialized models:

```text
Mistake classifier
Difficulty estimator
Mastery model
Retention model
```

---

### Stage 4

Potentially train:

```text
Personalized student model
Recommendation policy
Learning outcome predictor
```

---

# 50. Data Evolution

### Early

```text
PostgreSQL
```

### Intermediate

```text
PostgreSQL
+
pgvector
+
Redis
```

### Advanced

```text
Event Store
+
Analytics Store
+
Model Store
+
Vector Store
```

---

# 51. Testing Evolution

## Stage 1

Unit tests.

```text
Backend
Frontend
Execution
Database
```

## Stage 2

Integration tests.

```text
Event pipeline
Tutor pipeline
Problem generation
```

## Stage 3

Behavioral tests.

```text
Does the tutor respond correctly to student behavior?
```

## Stage 4

Learning-system evaluation.

```text
Does CodeAtlas actually make the student better?
```

---

# 52. Definition of Done

A feature is not complete simply because:

```text
It works.
```

For CodeAtlas a feature should ideally satisfy:

```text
Works
+
Tested
+
Observable
+
Secure
+
Documented
+
Measurable
```

For learning features add:

```text
+
Learning impact evaluated
```

---

# 53. Research Milestones

Potential research questions:

### RQ1

Can behavioral coding signals predict conceptual weaknesses?

### RQ2

Can mistake sequences predict future mistakes?

### RQ3

Can personalized hint policies reduce AI dependency?

### RQ4

Can adaptive retrieval improve long-term coding retention?

### RQ5

Can behavioral patterns predict when a student is about to get stuck?

### RQ6

Can CodeAtlas select problems that maximize learning gain?

### RQ7

Can personalized curriculum outperform static curriculum?

---

# 54. Possible Publications

Future research directions could lead toward papers involving:

```text
Personalized Programming Education
Adaptive Tutoring
Knowledge Tracing
Learning Analytics
AI-Assisted Programming
Human-AI Interaction
Educational Data Mining
Intelligent Tutoring Systems
```

Publication is not a primary development objective, but the architecture should make rigorous research possible.

---

# 55. Long-Term Vision

Eventually:

```text
                    CodeAtlas
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Observe        Understand      Predict
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                    Adapt
                       │
                       ▼
                    Teach
                       │
                       ▼
                   Evaluate
                       │
                       ▼
                  Learn About
                  The Learner
```

The system itself becomes adaptive.

---

# 56. Ultimate Architecture

The mature system should behave as a closed learning loop:

```text
┌───────────────────────────────────────┐
│                                       │
│              STUDENT                  │
│                                       │
└──────────────────┬────────────────────┘
                   │
                   ▼
              CODING ACTIVITY
                   │
                   ▼
               OBSERVATION
                   │
                   ▼
             EVIDENCE ENGINE
                   │
                   ▼
          ┌────────┴────────┐
          │                 │
          ▼                 ▼
     STUDENT MODEL     MISTAKE MODEL
          │                 │
          └────────┬────────┘
                   ▼
            LEARNING STATE
                   │
                   ▼
          ADAPTIVE POLICY
                   │
                   ▼
            NEXT ACTIVITY
                   │
                   ▼
               STUDENT
```

---

# 57. The Long-Term Goal

The mature CodeAtlas system should eventually understand:

```text
"I know what you are doing."

"I know where you are struggling."

"I know which mistakes are recurring."

"I know which concepts you are forgetting."

"I know when you are becoming dependent on hints."

"I know when you genuinely understand something."

"I know when you can transfer it to a new problem."

"I know what intervention is most likely to help."

"And I can measure whether my intervention actually worked."
```

---

# 58. Final Success Criterion

CodeAtlas succeeds only if:

```text
Student Capability ↑
AI Dependency ↓
```

over time.

The strongest possible outcome is:

```text
Month 1:
Student relies heavily on CodeAtlas.

Month 6:
Student uses it strategically.

Month 12:
Student solves increasingly difficult problems independently.

Month 18:
Student uses CodeAtlas primarily for advanced challenges and reflection.
```

The system should become a **scaffold**, not a permanent crutch.

---

# 59. Final Principle

> **Build the system that understands the learner, not merely the code.**

The IDE is the interface.

The AI tutor is the mechanism.

The adaptive curriculum is the engine.

The student model is the intelligence.

The learning outcome is the objective.

And the evidence stream is the foundation on which everything else depends.


# CodeAtlas — AI & ML Strategy

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define where AI/ML should be used, what should remain deterministic, how models learn from the student, and how the system evolves from an AI-assisted application into an adaptive learning system.

---

# 1. Purpose

CodeAtlas is not fundamentally an LLM application.

The core problem is:

> **Build a system that continuously estimates a student's programming knowledge, behavior, mistakes, retention, and learning needs, then adapts instruction accordingly.**

AI and ML are tools used to solve parts of this problem.

The architecture must therefore distinguish between:

Deterministic Software
        +
Statistical Models
        +
LLMs
        +
Student Interaction Data


rather than putting an LLM at the center of every operation.

---

# 2. Core Principle

The primary design principle is:

> **Use deterministic systems where correctness matters, ML where prediction matters, and LLMs where language/reasoning generation matters.**

For example:

```text
Code compilation
→ Deterministic

Test execution
→ Deterministic

Syntax analysis
→ Deterministic / AST

Mastery estimation
→ ML / probabilistic model

Problem selection
→ ML / optimization

Hint generation
→ LLM

Student explanation
→ LLM

Mistake classification
→ Hybrid
```

---

# 3. AI/ML Responsibilities

CodeAtlas should eventually use AI/ML for:

```text
1. Mistake classification
2. Skill inference
3. Mastery estimation
4. Forgetting estimation
5. Difficulty estimation
6. Problem selection
7. Problem generation
8. Hint generation
9. Explanation generation
10. Behavioral analysis
11. Code understanding
12. Transfer detection
13. Learning-gain prediction
14. Anomaly detection
15. Personalized tutoring
```

---

# 4. What Should NOT Require AI

Some tasks should remain deterministic.

```text
Compilation
Unit testing
Syntax checking
Code formatting
Execution limits
AST extraction
Cyclomatic complexity
Runtime measurement
Memory measurement
Git diff analysis
File tracking
Authentication
Authorization
Database operations
```

LLMs should not be used simply because they are available.

---

# 5. AI Architecture

```text
                    CodeAtlas
                       │
              ┌────────┴────────┐
              │                 │
        Deterministic       AI / ML Layer
           Layer                 │
              │          ┌───────┼────────┐
              │          │       │        │
              │         ML      LLM    Optimization
              │          │       │        │
              └──────────┴───────┴────────┘
                         │
                         ▼
                   Student Model
                         │
                         ▼
                  Adaptive Engine
```

---

# 6. Model Categories

CodeAtlas should use different models for different purposes.

```text
M1 — Rule-Based Models
M2 — Statistical Models
M3 — Classical ML
M4 — Deep Learning
M5 — Embedding Models
M6 — LLMs
M7 — Sequential / Bayesian Models
M8 — Recommendation / Policy Models
```

---

# 7. Version 1 AI Strategy

Version 1 should NOT attempt to build a massive custom ML system.

Recommended stack:

```text
Deterministic analysis
+
LLM API
+
Simple mastery model
+
Rule-based adaptation
+
Event logging
```

This gives a working learning loop while producing the data required for later ML.

---

# 8. Why Not Start With Deep Learning?

Because CodeAtlas initially has:

```text
1 student
```

and therefore:

```text
Very little training data.
```

A neural model trained on insufficient personal data would mostly learn noise.

Instead:

```text
Phase 1
Rules + Bayesian/statistical models

Phase 2
Classical ML

Phase 3
Sequential models

Phase 4
Personalized policy learning
```

---

# 9. Student Model

The most important AI component is the:

> **Student Model**

It represents the system's current belief about what the student knows and how they learn.

Conceptually:

```text
StudentState
{
    skills,
    subskills,
    mastery,
    confidence,
    retention,
    mistakes,
    behavior,
    preferences,
    learning_velocity,
    problem_history,
    hint_dependency,
    transfer_ability
}
```

---

# 10. Skill Representation

Skills should be represented as a graph rather than a flat list.

Example:

```text
Arrays
│
├── Traversal
├── Searching
├── Prefix Sum
├── Two Pointers
│   ├── Opposite Direction
│   └── Same Direction
└── Sliding Window
    ├── Fixed Window
    └── Dynamic Window
```

This allows CodeAtlas to reason about prerequisites.

---

# 11. Skill Mastery

Each skill should have an estimated mastery value:

```text
0.0 → No evidence
1.0 → Strong evidence
```

Example:

```text
Binary Search = 0.73
Sliding Window = 0.41
Recursion = 0.28
Hash Maps = 0.84
```

These values represent **belief**, not absolute truth.

---

# 12. Why Mastery Is Not a Score

A student solving:

```text
10 / 10
```

does not necessarily mean:

```text
Mastery = 100%
```

The problems may have been:

```text
too easy
too similar
heavily scaffolded
explicitly labeled
solved with hints
```

Therefore mastery must consider more evidence.

---

# 13. Mastery Evidence

Potential signals:

```text
Correctness
Independence
Problem Difficulty
Problem Novelty
Hint Usage
Time
Mistake Rate
Transfer Performance
Delayed Retrieval
Explanation Quality
Debugging Ability
```

---

# 14. Mastery Model

A simple initial model:

```text
Mastery =
w1(correctness)
+
w2(independence)
+
w3(difficulty)
+
w4(transfer)
+
w5(retention)
-
w6(hint_dependency)
-
w7(repeated_mistakes)
```

The weights should be experimentally calibrated.

---

# 15. Bayesian Knowledge Tracing

A strong candidate for CodeAtlas is:

> **Bayesian Knowledge Tracing (BKT)**

It models whether a student has learned a skill based on observed responses.

Conceptually:

```text
Before problem:
P(Knowledge)

Student solves problem

Evidence observed

After problem:
P(Knowledge | Evidence)
```

---

# 16. BKT Variables

Traditional BKT uses parameters such as:

```text
P(L0) — initial knowledge
P(T)  — probability of learning
P(S)  — probability of slip
P(G)  — probability of guess
```

CodeAtlas can later extend this representation.

---

# 17. Limitations of BKT

Traditional BKT assumes relatively simple learning behavior.

It may not fully represent:

```text
complex programming skills
multiple interacting skills
behavior
different problem difficulty
hint dependency
transfer
forgetting
```

Therefore BKT should be treated as a starting point.

---

# 18. Item Response Theory

Another useful framework is:

> **Item Response Theory (IRT)**

IRT models the relationship between:

```text
Student ability
+
Problem difficulty
```

and probability of success.

Conceptually:

```text
P(correct | ability, difficulty)
```

---

# 19. Why IRT Matters

Suppose:

```text
Student A solves a hard problem.
Student B solves an easy problem.
```

Both may receive:

```text
Correct = true
```

But the evidence is not equally informative.

IRT provides a mathematical framework for accounting for this.

---

# 20. IRT + BKT

CodeAtlas may eventually combine:

```text
BKT
+
IRT
+
Forgetting Model
```

to estimate:

```text
Current Knowledge
+
Problem Difficulty
+
Retention
```

This is significantly stronger than simple accuracy.

---

# 21. Knowledge Tracing Evolution

Potential progression:

```text
V1
Rule-based mastery

V2
BKT

V3
IRT + BKT

V4
Deep Knowledge Tracing

V5
Personalized sequential model
```

---

# 22. Deep Knowledge Tracing

Later, CodeAtlas can investigate:

> **Deep Knowledge Tracing (DKT)**

A recurrent or transformer-based model can learn patterns across sequences of student interactions.

Input:

```text
Problem 1 → correct
Problem 2 → wrong
Problem 3 → hint
Problem 4 → correct
...
```

Output:

```text
Estimated mastery for skills
```

---

# 23. Why DKT Should Be Later

DKT requires substantially more interaction data.

With one student:

```text
Model complexity > available evidence
```

is likely.

Therefore:

> **Do not use deep knowledge tracing simply because it sounds advanced.**

---

# 24. Forgetting Model

Learning and forgetting are different processes.

CodeAtlas should estimate:

```text
Current Mastery
```

and:

```text
Probability of Successful Retrieval
```

separately.

A student can have:

```text
High learned knowledge
+
low current retrieval
```

---

# 25. Forgetting Function

A simple initial model can use exponential decay:

```text
R(t) = e^(-t/S)
```

where:

```text
R(t) = estimated retention
t = time since learning
S = memory stability
```

Later, CodeAtlas can learn personalized stability parameters.

---

# 26. Personalized Forgetting

Different concepts decay differently.

Example:

```text
Python syntax:
high retention

Dynamic Programming:
lower retention
```

The system should eventually learn:

```text
Student × Skill
```

specific forgetting patterns.

---

# 27. Behavioral Modeling

CodeAtlas should model behavior separately from knowledge.

Examples:

```text
Rushes to code
Overuses hints
Doesn't test
Overengineers
Copies solutions
Abandons quickly
Doesn't read requirements
Changes code randomly
```

These are not necessarily knowledge deficits.

---

# 28. Behavioral Features

Possible features:

```text
time_to_first_code
time_to_first_test
number_of_edits
number_of_revisions
hint_latency
attempt_count
test_frequency
solution_reveal_rate
debugging_sequence
```

---

# 29. Behavioral Classification

Initial approach:

```text
Rules
+
thresholds
+
statistical analysis
```

Later:

```text
Classification Model
```

Potential models:

```text
Logistic Regression
Random Forest
Gradient Boosting
Sequence Models
```

---

# 30. Mistake Classification

Mistakes should combine deterministic and AI analysis.

Pipeline:

```text
Student Code
    │
    ├── Compiler
    ├── Tests
    ├── AST
    ├── Diff
    └── LLM Analysis
            │
            ▼
       Mistake Classifier
```

---

# 31. Deterministic Mistake Detection

Examples:

```text
Syntax error
Compilation failure
Runtime exception
Timeout
Wrong output
Failed assertion
```

These can often be detected without AI.

---

# 32. Semantic Mistake Detection

Examples:

```text
Wrong algorithm
Misunderstood requirement
Incorrect invariant
Poor abstraction
Overengineering
```

These may require:

```text
LLM
+
static analysis
+
problem metadata
```

---

# 33. Hybrid Mistake Classifier

Example:

```text
Test Failure
     │
     ▼
AST + Runtime Analysis
     │
     ▼
Candidate Mistakes
     │
     ▼
LLM Semantic Analysis
     │
     ▼
Final Classification
```

---

# 34. LLM Role

LLMs should primarily handle:

```text
Natural language understanding
Code explanation
Hint generation
Problem generation
Mistake interpretation
Tutoring dialogue
Requirement interpretation
Conceptual explanation
```

---

# 35. LLM Should Not Be the Source of Truth

For example:

Bad:

```text
LLM:
"Your code is correct."
```

without execution.

Good:

```text
Compiler
+
Tests
+
Runtime
+
Static Analysis
+
LLM Explanation
```

The execution environment decides correctness.

---

# 36. LLM Provider Abstraction

CodeAtlas should not hard-code one provider.

Architecture:

```text
LLMProvider
   │
   ├── Gemini
   ├── Groq
   ├── OpenAI-compatible API
   ├── Local Model
   └── Future Providers
```

---

# 37. Model Routing

Different tasks may use different models.

Example:

```text
Simple classification
→ cheap/small model

Hint generation
→ medium model

Complex debugging
→ stronger model

Problem generation
→ strong reasoning model

Embedding
→ embedding model
```

This reduces cost.

---

# 38. LLM Cost Strategy

Do not send the entire student history to the LLM.

Instead:

```text
Raw History
    ↓
Feature Extraction
    ↓
Student State
    ↓
Relevant Context
    ↓
LLM
```

Only relevant information should enter the prompt.

---

# 39. Context Construction

Example:

```text
Current Problem
+
Current Code
+
Recent Errors
+
Relevant Skill
+
Known Mistakes
+
Tutor State
```

rather than:

```text
Entire Database
```

---

# 40. Prompt Architecture

Prompts should be structured.

```text
SYSTEM
    Tutor rules

STUDENT STATE
    Relevant learning information

TASK
    Current objective

PROBLEM
    Current problem

CODE
    Student's current code

OBSERVATIONS
    Tests / errors / behavior

OUTPUT FORMAT
    Required response schema
```

---

# 41. Structured LLM Output

LLMs should return structured objects where possible.

Example:

```text
MistakeAnalysis
{
    primary_category,
    secondary_categories,
    evidence,
    confidence,
    recommended_action
}
```

Avoid depending on free-form text for critical system logic.

---

# 42. Confidence

AI predictions should include confidence.

Example:

```text
Mistake:
Off-by-one

Confidence:
0.87
```

Low-confidence predictions can trigger:

```text
additional analysis
```

instead of immediately changing the curriculum.

---

# 43. Uncertainty

CodeAtlas should explicitly model uncertainty.

Example:

```text
Binary Search mastery:
0.72

Confidence:
0.41
```

This means:

```text
The system believes mastery is moderate,
but does not have enough evidence.
```

This is different from:

```text
Mastery = 0.72 with confidence = 0.95
```

---

# 44. Exploration vs Exploitation

The adaptive engine faces:

```text
Exploration:
Test something we don't know about the student.

Exploitation:
Practice something we already know is weak.
```

CodeAtlas must balance both.

---

# 45. Example

Known weakness:

```text
Sliding Window = 0.35
```

The system should not give:

```text
100% sliding-window problems.
```

It should occasionally test:

```text
graphs
recursion
DP
```

to discover hidden weaknesses.

---

# 46. Multi-Armed Bandit

A future approach is:

> **Contextual Multi-Armed Bandits**

Each possible activity is an action:

```text
A1 — Practice
A2 — Retrieval
A3 — Debugging
A4 — Explanation
A5 — Transfer
```

The system estimates expected learning value.

---

# 47. Reward Definition

Potential reward:

```text
Learning Gain
+
Retention Improvement
+
Transfer Improvement
+
Independence
-
Time Cost
-
Frustration
```

The reward must not simply be:

```text
Problem solved = +1
```

because that encourages easy problems.

---

# 48. Problem Selection Model

Eventually:

```text
Student State
      +
Candidate Problems
      ↓
Prediction Model
      ↓
Expected Learning Gain
      ↓
Selection Policy
```

---

# 49. Learning Gain

CodeAtlas should distinguish:

```text
Performance
```

from:

```text
Learning
```

A student may solve a problem correctly because they memorized the pattern.

Learning is better demonstrated through:

```text
Delayed retrieval
+
novel problem
+
transfer
```

---

# 50. Transfer Detection

Suppose:

```text
Student learned sliding window.
```

CodeAtlas later presents:

```text
string problem
```

If the student independently identifies the same reasoning:

```text
Transfer = strong
```

This is valuable evidence of actual understanding.

---

# 51. AI Evaluation of Explanations

LLMs can evaluate whether the student's explanation demonstrates:

```text
conceptual understanding
```

rather than:

```text
memorized terminology
```

However, explanation evaluation should be validated against structured rubrics.

---

# 52. Rubric-Based Evaluation

Example:

```text
Algorithm Explanation

1. Identifies invariant
2. Explains state
3. Explains transition
4. Explains correctness
5. Explains complexity
```

Score each dimension separately.

---

# 53. Code Embeddings

CodeAtlas may use embeddings to represent:

```text
student code
solutions
problems
explanations
mistakes
```

Possible uses:

```text
similarity detection
duplicate detection
solution clustering
problem retrieval
semantic search
```

---

# 54. Code Embeddings Are Not Correctness

Embedding similarity cannot prove:

```text
code correctness
```

It can only provide semantic similarity evidence.

Correctness still comes from:

```text
execution
tests
formal/static analysis
```

where applicable.

---

# 55. Retrieval-Augmented Generation

The tutor may use RAG.

Possible knowledge sources:

```text
Student's previous mistakes
Previous solved problems
Relevant concepts
Learning notes
CodeAtlas documentation
Validated explanations
```

Pipeline:

```text
Current Situation
      ↓
Retrieve Relevant Context
      ↓
LLM
      ↓
Personalized Response
```

---

# 56. Personalized Memory

CodeAtlas should maintain structured memory such as:

```text
"Student repeatedly forgets binary-search boundaries."
```

rather than storing every conversation indefinitely.

---

# 57. Memory Hierarchy

```text
Raw Events
    ↓
Session Summaries
    ↓
Behavior Patterns
    ↓
Mistake Patterns
    ↓
Learning State
```

The higher-level representation should be used for adaptation.

---

# 58. AI Memory Should Be Evidence-Based

A memory should ideally include:

```text
Observation
Frequency
Confidence
Last Seen
Evidence
```

Example:

```text
Pattern:
Off-by-one errors

Frequency:
7

Last observed:
2026-08-20

Confidence:
0.91
```

---

# 59. Avoiding False Personalization

CodeAtlas should not conclude:

```text
"Student is bad at recursion."
```

after:

```text
one failed recursion problem.
```

It should require sufficient evidence.

---

# 60. Evidence Thresholds

Example:

```text
1 failure:
Weak evidence

3 similar failures:
Moderate evidence

Repeated failures across variations:
Strong evidence
```

Exact thresholds should be empirically determined.

---

# 61. Personalization Without Overfitting

The system must distinguish:

```text
Temporary failure
```

from:

```text
Stable weakness
```

Possible causes of temporary failure:

```text
fatigue
distraction
ambiguous problem
unfamiliar syntax
environment issue
```

Therefore context matters.

---

# 62. Cold Start

At the beginning:

```text
CodeAtlas knows almost nothing.
```

It should therefore perform a short diagnostic.

Example:

```text
Arrays
Loops
Functions
Recursion
Complexity
Searching
Sorting
Basic DSA
```

The diagnostic should cover broad skills efficiently.

---

# 63. Cold-Start Strategy

Do not ask:

```text
100 questions.
```

Instead:

```text
Small diagnostic set
+
adaptive branching
```

If the student demonstrates strong knowledge:

```text
skip basics
```

If weak:

```text
probe deeper
```

---

# 64. AI During Diagnostic

The system can estimate:

```text
initial mastery
```

but should maintain uncertainty until enough evidence exists.

---

# 65. Continuous Learning

The student's model should update after:

```text
every meaningful interaction
```

Examples:

```text
problem solved
hint requested
test written
mistake corrected
concept explained
transfer succeeded
```

---

# 66. Event-Driven Learning Updates

Architecture:

```text
Student Event
      ↓
Event Processor
      ↓
Feature Extraction
      ↓
Model Update
      ↓
Student State
      ↓
Adaptive Engine
```

This allows CodeAtlas to react quickly.

---

# 67. Feature Store

Useful derived features:

```text
average_solution_time
hint_rate
test_rate
revision_rate
mistake_frequency
skill_success_rate
transfer_success_rate
retention_success_rate
```

These should be computed rather than repeatedly inferred by an LLM.

---

# 68. Model Registry

As CodeAtlas evolves, models should be versioned.

```text
models/
├── mastery/
├── mistake_classifier/
├── difficulty/
├── embeddings/
└── recommendation/
```

Each model should record:

```text
version
training data
metrics
parameters
deployment date
```

---

# 69. Offline vs Online Learning

Version 1:

```text
Offline analysis
+
rule-based updates
```

Later:

```text
Online model updates
```

Eventually:

```text
Continuous personalization
```

---

# 70. Model Training Data

Potential data sources:

```text
Student interaction events
Public coding datasets
Curated programming problems
Synthetic tutoring interactions
Code execution traces
Expert annotations
```

---

# 71. Synthetic Data

Synthetic data can help bootstrap:

```text
mistake classification
problem generation
hint evaluation
```

But synthetic data should not be treated as equivalent to real student behavior.

---

# 72. Human Evaluation

Important components require expert review.

Especially:

```text
Problem quality
Mistake classification
Hint quality
Learning objective alignment
Mastery estimates
```

---

# 73. AI Evaluation Metrics

## Mistake Classification

```text
Precision
Recall
F1
Confusion Matrix
Calibration
```

## Problem Generation

```text
Validity
Correctness
Difficulty accuracy
Skill alignment
Diversity
```

## Mastery Model

```text
Prediction accuracy
Calibration
Longitudinal consistency
```

## Tutor

```text
Learning gain
Hint efficiency
Independence
Student retention
```

---

# 74. Calibration

A prediction of:

```text
80% chance of success
```

should actually succeed approximately:

```text
80% of the time
```

across comparable cases.

Calibration is critical for adaptive systems.

---

# 75. Hallucination Handling

If an LLM produces uncertain information:

```text
Confidence low
```

CodeAtlas should:

```text
ask for more evidence
```

or:

```text
use deterministic verification
```

rather than confidently acting on the prediction.

---

# 76. AI Safety

Code execution must be sandboxed.

LLM output must be treated as untrusted input.

The system must prevent:

```text
prompt injection
unsafe code execution
data leakage
secret exposure
cross-user data leakage
```

---

# 77. Privacy-Aware AI

The system should minimize what is sent to external APIs.

Possible strategy:

```text
Raw code
    ↓
Sanitization
    ↓
Relevant context extraction
    ↓
LLM API
```

---

# 78. Local AI

Future versions should support local models.

Potential architecture:

```text
CodeAtlas
   │
   ├── Cloud LLM
   │
   └── Local LLM
```

This provides:

```text
privacy
offline capability
lower marginal cost
```

---

# 79. Model Routing by Privacy

Sensitive project code:

```text
Local model preferred
```

Generic problem explanation:

```text
Cloud model acceptable
```

This decision should be policy-driven.

---

# 80. Explainability of AI Decisions

CodeAtlas should be able to answer:

> "Why did you give me this problem?"

Example:

```text
Because:

• You made 3 boundary errors recently.
• Your two-pointer mastery is estimated at 0.46.
• You have not practiced it for 8 days.
• You solved similar problems only when the technique was explicitly named.
```

This is crucial.

---

# 81. Explainable Adaptation

The system should not behave like:

```text
Black Box
↓
Random Problem
```

Instead:

```text
Evidence
↓
Inference
↓
Decision
```

should be inspectable.

---

# 82. AI Decision Trace

Each adaptation decision can store:

```text
Decision
Reason
Evidence
Model
Confidence
Alternatives
```

Example:

```text
Decision:
Give retrieval problem

Reason:
High forgetting risk

Confidence:
0.88
```

---

# 83. Research Direction

CodeAtlas can eventually become a research platform for:

```text
Personalized programming education
Knowledge tracing
Adaptive curriculum
AI tutoring
Human-AI learning
Code behavior modeling
Learning-to-learn systems
```

---

# 84. Recommended Technical Stack

## Version 1

```text
Frontend:
React / Next.js

Backend:
FastAPI

Database:
PostgreSQL

Execution:
Docker sandbox

LLM:
Gemini / Groq / OpenAI-compatible provider

Embeddings:
Sentence Transformers

Vector Store:
FAISS / pgvector

Analytics:
Python

ML:
scikit-learn
```

---

# 85. Version 2

Add:

```text
BKT
IRT
Feature Store
Model Registry
Advanced recommendation engine
Semantic code analysis
```

---

# 86. Version 3

Add:

```text
Knowledge Graph
Deep Knowledge Tracing
Contextual Bandits
Personalized forgetting model
Advanced code embeddings
```

---

# 87. Version 4

Research-level capabilities:

```text
Personalized learning policy
Online adaptation
Learning-gain prediction
Multi-objective optimization
Repository-level tutoring
Self-improving curriculum
```

---

# 88. Recommended Model Strategy

Do not attempt:

```text
One Giant AI
```

Instead:

```text
                 CodeAtlas AI
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
  Student Model   Tutor Model   Problem Model
       │              │              │
       ▼              ▼              ▼
   Mastery        LLM/RAG       Generation
   Retention      Hints         Selection
   Behavior       Explain       Difficulty
       │              │              │
       └──────────────┼──────────────┘
                      ▼
               Adaptive Policy
```

---

# 89. What Makes This Different From Copilot

Copilot optimizes:

```text
"Help me write this code."
```

CodeAtlas optimizes:

```text
"Help me become better at writing code."
```

Therefore the AI objective is different.

Copilot:

```text
Task Completion
```

CodeAtlas:

```text
Learning Progress
```

---

# 90. Core AI Loop

```text
Observe
   ↓
Infer
   ↓
Decide
   ↓
Teach
   ↓
Measure
   ↓
Update
   ↓
Repeat
```

This loop is the AI heart of CodeAtlas.

---

# 91. Final Principle

The most important architectural decision is:

> **CodeAtlas should not optimize for the student getting today's problem right. It should optimize for the student needing CodeAtlas less tomorrow.**

That means the system must reward:

```text
independence
+
transfer
+
retention
+
reasoning
```

rather than:

```text
answer completion
```

---

# 92. Long-Term AI Vision

The eventual CodeAtlas system should behave like:

```text
                 STUDENT
                    │
                    ▼
                OBSERVATION
                    │
                    ▼
             PERSONAL MODEL
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       MASTERY   BEHAVIOR  RETENTION
          │         │         │
          └─────────┼─────────┘
                    ▼
             LEARNING STATE
                    │
                    ▼
            ADAPTIVE POLICY
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       PROBLEM     TUTOR    RETRIEVAL
          │         │         │
          └─────────┼─────────┘
                    ▼
                 STUDENT
                    │
                    ▼
                 EVIDENCE
                    │
                    └──────────► UPDATE
```

The intelligence of CodeAtlas is therefore not contained inside one model.

It emerges from the **closed-loop interaction between observation, modeling, decision-making, tutoring, and measurement**.

# CodeAtlas — Product Requirements Document

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Product Type:** Personal Adaptive Coding Intelligence System  
> **Primary User:** Single student / programmer  
> **Initial Platform:** Web Application  
> **AI:** External LLM APIs through an abstraction layer

---

# 1. Product Overview

CodeAtlas is a personal AI-powered coding tutor designed to understand **how an individual programmer learns**, rather than simply helping them write code.

The system combines a web-based IDE, code execution, behavioral observation, mistake analysis, learner modeling, adaptive curriculum generation, tutoring, retention modeling, and personalized problem generation.

The product continuously follows this loop:

```text
Student
   ↓
Codes
   ↓
System observes
   ↓
Evidence extracted
   ↓
Learner model updated
   ↓
Weaknesses / patterns identified
   ↓
Next learning objective selected
   ↓
Problem / intervention generated
   ↓
Student practices
   ↓
Learning evaluated
   ↓
Learner model updated
   ↓
Repeat
````

The product's success is measured by **improvement in the student's independent programming ability**, not by AI usage or number of generated questions.

---

# 2. Product Vision

CodeAtlas should eventually become a system capable of answering:

```text
What does this programmer know?

What does this programmer not know?

What are they forgetting?

What mistakes do they repeatedly make?

How do they approach problems?

How do they debug?

Where does their reasoning break?

What kind of help works best for them?

What should they practice next?

Did the intervention actually improve them?

Can they solve a new problem without assistance?
```

The long-term goal is to create a **personal computational model of programming ability and learning behavior**.

---

# 3. Product Goals

## 3.1 Primary Goals

CodeAtlas must:

1. Provide a functional web-based coding environment.
2. Allow students to solve programming problems.
3. Execute code safely.
4. Observe meaningful coding activity.
5. Track coding behavior.
6. Detect and classify mistakes.
7. Represent programming competency at sub-skill level.
8. Build a persistent learner model.
9. Generate personalized practice.
10. Adapt problem difficulty.
11. Provide adaptive tutoring.
12. Track knowledge retention.
13. Detect recurring weaknesses.
14. Evaluate transfer to unfamiliar problems.
15. Measure improvement over time.

---

# 4. Non-Goals

CodeAtlas is explicitly **not** intended to become the following.

## 4.1 Copilot Clone

The primary goal is not autocomplete or code generation.

## 4.2 Generic Chatbot

The tutor must be grounded in learner state and problem context.

## 4.3 LeetCode Clone

The product is not primarily a problem repository.

## 4.4 Static Course Platform

The curriculum must adapt to the learner.

## 4.5 AI Answer Machine

The system should avoid immediately solving every problem for the student.

## 4.6 Engagement Maximizer

The product should optimize learning rather than:

```text
screen time
streak length
number of interactions
number of AI messages
```

## 4.7 Surveillance Tool

Behavioral tracking exists to improve learning and must remain privacy-conscious.

---

# 5. Target User

## Primary User

A single student/programmer who wants to improve programming ability through deliberate practice.

The initial architecture intentionally supports one highly personalized learner.

This allows CodeAtlas to focus on:

```text
depth > breadth
personalization > scale
learning quality > user count
```

Multi-user support may be introduced later.

---

# 6. Core User Journey

A typical user journey should look like:

```text
Open CodeAtlas
      ↓
View current learning state
      ↓
Receive today's recommended objective
      ↓
Open recommended problem
      ↓
Read requirements
      ↓
Plan solution
      ↓
Write code
      ↓
Run tests
      ↓
Debug
      ↓
Ask for help if necessary
      ↓
Complete / abandon problem
      ↓
Receive learning analysis
      ↓
Reflect
      ↓
Receive next recommendation
```

The system should remember what happened during this session.

---

# 7. Product Modules

CodeAtlas consists of the following major modules.

```text
┌────────────────────────────────────┐
│             CodeAtlas              │
├────────────────────────────────────┤
│                                    │
│  1. Web IDE                        │
│  2. Code Execution                 │
│  3. Problem System                 │
│  4. Observation System             │
│  5. Mistake Detection              │
│  6. Behavior Modeling              │
│  7. Learner Model                  │
│  8. Adaptive Curriculum             │
│  9. Tutoring Engine                │
│ 10. Problem Generator              │
│ 11. Retention System               │
│ 12. Evaluation System              │
│ 13. Analytics Dashboard             │
│ 14. AI Gateway                     │
│                                    │
└────────────────────────────────────┘
```

---

# 8. Functional Requirements

---

# FR-001 — User Profile

The system shall maintain a persistent profile for the student.

The profile should contain:

```text
User identity
Programming languages
Current skill state
Learning history
Mistake history
Behavior history
Retention information
Curriculum state
Preference information
```

The profile must be extensible.

---

# FR-002 — Web-Based IDE

The system shall provide an integrated coding environment.

The IDE should support:

* Code editor
* Syntax highlighting
* Language selection
* Run button
* Test execution
* Output display
* Error display
* File management
* Problem statement panel
* Tutor panel

Initial supported languages should be limited.

A language should be added only when CodeAtlas can reliably:

* parse it
* execute it
* analyze it
* identify relevant errors

---

# FR-003 — Problem Interface

Every coding problem shall contain structured metadata.

Example:

```text
Problem
├── title
├── description
├── constraints
├── examples
├── topic
├── subskills
├── prerequisites
├── difficulty
├── expected_complexity
├── learning_objective
├── common_mistakes
└── evaluation_strategy
```

The student should not necessarily see all metadata.

Some metadata exists for the learning engine.

---

# FR-004 — Code Execution

The system shall execute submitted code inside an isolated environment.

The execution environment must enforce:

```text
CPU limits
Memory limits
Execution timeout
Process limits
Filesystem restrictions
Network restrictions
```

The execution system must never execute arbitrary student code directly on the main application server.

---

# FR-005 — Coding Event Tracking

The system shall capture meaningful coding events.

Examples:

```text
PROBLEM_STARTED
CODE_EDITED
CODE_EXECUTED
TEST_CREATED
TEST_EXECUTED
TEST_FAILED
TEST_PASSED
ERROR_OCCURRED
HINT_REQUESTED
QUESTION_ASKED
SOLUTION_VIEWED
ALGORITHM_CHANGED
CODE_REVERTED
PROBLEM_COMPLETED
PROBLEM_ABANDONED
SESSION_STARTED
SESSION_ENDED
```

Events should contain timestamps and contextual information.

---

# FR-006 — Code Revision Tracking

The system shall preserve meaningful code revisions.

A revision should capture:

```text
revision_id
timestamp
source_code
parent_revision
trigger
execution_result
```

The system should avoid creating unnecessary revisions for every keystroke.

The observation layer may aggregate rapid edits.

---

# FR-007 — Mistake Detection

The system shall identify programming mistakes.

Initial taxonomy:

```text
Syntax Error
Logic Error
Off-by-One Error
Wrong Algorithm
Complexity Mistake
Requirement Misunderstanding
Repeated Mistake
Copying Solution
Overengineering
Testing Failure
Edge Case Failure
Incorrect Assumption
```

Mistake detection may combine:

```text
Static Analysis
Dynamic Analysis
Test Results
Problem Metadata
Behavioral Evidence
LLM Analysis
```

---

# FR-008 — Mistake Confidence

Every automatically detected mistake should have a confidence value.

Example:

```text
mistake:
OFF_BY_ONE

confidence:
0.87

evidence:
- failing boundary test
- incorrect loop bound
- similar previous mistake
```

The system should distinguish:

```text
Observed fact
```

from:

```text
Inference
```

---

# FR-009 — Repeated Mistake Detection

The system shall identify recurring mistake patterns.

Example:

```text
Week 1:
Binary search → off-by-one

Week 2:
Two pointer → boundary error

Week 3:
Sliding window → boundary error
```

The system may infer:

```text
Potential weakness:
Boundary reasoning
```

However, repeated evidence should be required before making strong learner-state changes.

---

# FR-010 — Skill Model

The system shall maintain programming skills at multiple levels.

Example:

```text
Algorithms
│
├── Searching
│   ├── Linear Search
│   └── Binary Search
│       ├── Recognition
│       ├── Implementation
│       ├── Boundary Handling
│       └── Complexity
│
├── Sorting
│
└── Graph Algorithms
```

A skill should have multiple attributes.

Example:

```text
mastery
confidence
evidence_count
recent_success
recent_failure
retention
trend
```

---

# FR-011 — Learner Model

The learner model shall combine:

```text
Skill State
+
Mistake State
+
Behavior State
+
Retention State
+
Intervention History
```

The model should be updated after meaningful learning events.

---

# FR-012 — Behavior Modeling

CodeAtlas shall model useful programming behaviors.

Initial behavioral signals:

```text
Time to first attempt
Time to solve
Attempts
Revision count
Execution frequency
Testing behavior
Hint dependency
Question frequency
Debugging behavior
Algorithm switching
Solution copying
Overengineering
```

The system should focus on patterns rather than isolated actions.

---

# FR-013 — Hint System

The tutor shall support graduated assistance.

Initial hierarchy:

```text
Level 0
No assistance

Level 1
Reflective prompt

Level 2
Small hint

Level 3
Targeted hint

Level 4
Concept explanation

Level 5
Guided reasoning

Level 6
Partial solution

Level 7
Worked solution
```

The system should avoid immediately jumping to Level 7.

---

# FR-014 — Adaptive Tutoring

The tutor shall select an intervention based on:

```text
Current problem
Current mistake
Learner skill
Previous mistakes
Hint history
Behavior
Previous interventions
Learning objective
```

Possible interventions:

```text
Hint
Socratic Question
Diagnostic Question
Concept Explanation
Debugging Guidance
Worked Example
Reflection
Challenge
```

---

# FR-015 — Repeated Tutoring

If the student has not demonstrated sufficient understanding, the system may revisit the concept.

However, it must have stopping conditions.

Example:

```text
Attempt
 ↓
Hint
 ↓
Retry
 ↓
Still confused
 ↓
Concept intervention
 ↓
Retry
 ↓
Still confused
 ↓
Worked example
 ↓
New related problem
```

The system must avoid trapping the student indefinitely on one problem.

---

# FR-016 — Adaptive Difficulty

Every problem should have a difficulty estimate.

Difficulty should eventually be based on more than a manually assigned label.

Potential signals:

```text
historical solve rate
average attempts
average solve time
hint requirement
mistake frequency
skill prerequisites
transfer difficulty
```

The difficulty should adapt to the individual student.

---

# FR-017 — Personalized Curriculum

The system shall generate a personalized practice schedule.

Initial recommendation:

```text
40% Weakness reinforcement
30% New learning
20% Forgotten concepts
10% Mastered concepts
```

This distribution should eventually become dynamic.

---

# FR-018 — Forgetting Detection

The system shall estimate whether previously learned concepts may be decaying.

Possible evidence:

```text
Time since last practice
Recent retrieval failure
Repeated mistakes
Reduced performance
Increased hint usage
Transfer failure
```

The system should distinguish:

```text
Never learned
```

from:

```text
Previously learned but potentially forgotten
```

---

# FR-019 — Retention Scheduling

The system shall schedule review opportunities.

A concept should not simply disappear after being marked mastered.

Example:

```text
Mastered
   ↓
Delayed review
   ↓
Successful retrieval
   ↓
Longer interval
```

or:

```text
Mastered
   ↓
Delayed review
   ↓
Failure
   ↓
Shorter interval
```

---

# FR-020 — Problem Generation

The system shall generate or select problems based on learner state.

Problem generation modes:

```text
Skill Practice
Weakness Practice
Mistake Correction
Retention Practice
Transfer Practice
Difficulty Challenge
Mixed Practice
```

Generated problems must be validated before being presented.

---

# FR-021 — Problem Validation

AI-generated problems must pass validation.

Validation should check:

```text
Problem completeness
Logical consistency
Constraint correctness
Example correctness
Expected output correctness
Solution validity
Test-case validity
Difficulty metadata
Learning objective alignment
```

The LLM should not be trusted as the sole validator.

---

# FR-022 — Transfer Evaluation

The system shall periodically provide unfamiliar problems that target previously learned skills.

Example:

```text
Previously practiced:
Binary search in sorted arrays

Transfer:
Search over an answer space
```

The surface problem changes while the underlying reasoning is related.

Transfer performance should influence the learner model.

---

# FR-023 — Learning Dashboard

The dashboard shall display:

```text
Current strengths
Current weaknesses
Skill progression
Recent mistakes
Retention risks
Recommended practice
Learning streak
Recent achievements
Problem-solving trends
```

The dashboard should avoid misleading certainty.

---

# FR-024 — Recommendation Explanation

When useful, CodeAtlas should explain why something was recommended.

Example:

```text
Recommended because:

• You made 3 recent boundary mistakes.
• Boundary handling is currently estimated below your target.
• You have not practiced this skill for 8 days.
• Your last transfer attempt was unsuccessful.
```

---

# FR-025 — AI Provider Abstraction

The system shall communicate with LLM providers through an AI gateway.

Architecture:

```text
Tutor Engine
      ↓
AI Gateway
      ↓
Provider Adapter
      ↓
Gemini / Groq / Other
```

The rest of CodeAtlas should not depend directly on a specific provider.

---

# FR-026 — AI Context Management

The system shall provide relevant context to the AI rather than blindly sending the entire learner history.

Context may include:

```text
Current problem
Current code
Current error
Relevant skill state
Recent mistakes
Relevant behavioral patterns
Previous tutor interaction
Current learning objective
```

Context should be selected dynamically.

---

# FR-027 — AI Response Validation

AI responses should be validated before being used by the application.

Validation may include:

```text
Schema validation
Safety validation
Problem-context validation
Code validation
Instruction validation
Hallucination checks
```

---

# FR-028 — Session Summary

At the end of a meaningful coding session, CodeAtlas shall generate structured session information.

Example:

```text
Session
├── Problems attempted
├── Problems solved
├── Mistakes
├── Skills practiced
├── Hints requested
├── Time spent
├── Tests written
├── Behavioral observations
├── Interventions
└── Learning outcomes
```

---

# FR-029 — Historical Learning Record

CodeAtlas shall maintain a longitudinal history.

The student should be able to inspect how they have changed over time.

Examples:

```text
August:
Frequent recursion errors

September:
Reduced recursion errors

October:
Successful transfer to tree problems
```

---

# FR-030 — Adaptive State Updates

The learner model should update incrementally rather than being rebuilt blindly after every interaction.

Each update should have:

```text
Evidence
Change
Reason
Confidence
Timestamp
```

---

# 9. Non-Functional Requirements

---

# NFR-001 — Performance

Normal IDE interactions should feel responsive.

Target:

```text
Code editor interaction:
< 100 ms perceived local response

API requests:
preferably < 500 ms where no LLM is involved

LLM response:
dependent on provider
```

AI latency should not block normal IDE operations.

---

# NFR-002 — Reliability

The core coding environment should remain usable if the external AI provider is temporarily unavailable.

For example:

```text
Gemini unavailable
      ↓
IDE still works
      ↓
Code execution still works
      ↓
Learning events still recorded
      ↓
AI tutoring temporarily unavailable
```

This is an important architectural property.

---

# NFR-003 — Security

The system must:

* isolate code execution
* protect authentication credentials
* encrypt sensitive data where appropriate
* restrict API access
* validate user input
* prevent prompt injection from compromising system behavior
* avoid exposing secrets to the LLM
* protect student source code

---

# NFR-004 — Privacy

Student data must be collected according to purpose.

Potentially sensitive data includes:

```text
Source code
Learning history
Mistake history
Behavioral data
AI conversations
Performance data
```

The system should support data deletion and export.

---

# NFR-005 — Explainability

Important learner-state changes should be traceable to evidence.

The system should be able to answer:

```text
Why did my mastery score change?

Why was this problem recommended?

Why did the tutor give this hint?

Why did CodeAtlas classify this as a recurring mistake?
```

---

# NFR-006 — Extensibility

The architecture must support:

```text
New programming languages
New LLM providers
New mistake types
New learning models
New curriculum strategies
New evaluation methods
New ML models
```

without requiring major architectural rewrites.

---

# NFR-007 — Reproducibility

Learning decisions should be reproducible as much as practical.

Important decisions should retain:

```text
Input state
Evidence
Policy version
Model version
Decision
Timestamp
```

---

# 10. MVP Definition

The first usable CodeAtlas version should NOT attempt to implement the entire long-term vision.

The MVP should establish the fundamental learning loop.

## MVP Components

```text
Web IDE
+
Code Execution
+
Problem System
+
Event Tracking
+
Basic Mistake Detection
+
Basic Skill Model
+
AI Tutor
+
Basic Adaptive Recommendations
+
Learning Dashboard
```

---

# 11. MVP Learning Loop

The minimum viable intelligence should be:

```text
Student solves problem
       ↓
System records activity
       ↓
Mistake identified
       ↓
Skill evidence generated
       ↓
Learner state updated
       ↓
Next problem selected
       ↓
Student solves again
```

If this loop works reliably, additional intelligence can be layered on top.

---

# 12. Version 1 Feature Priorities

## P0 — Essential

These features are required for the first functioning learning system.

```text
[ ] Web IDE
[ ] Code execution
[ ] Problem system
[ ] User profile
[ ] Session tracking
[ ] Event tracking
[ ] Submission history
[ ] Basic mistake detection
[ ] Basic skill tracking
[ ] AI tutor
[ ] Basic recommendations
```

---

## P1 — Important

```text
[ ] Code revision analysis
[ ] Behavioral analysis
[ ] Sub-skill model
[ ] Adaptive difficulty
[ ] Personalized curriculum
[ ] Hint escalation
[ ] Learning dashboard
[ ] Recommendation explanations
[ ] Retention scheduling
```

---

## P2 — Advanced

```text
[ ] Transfer evaluation
[ ] Problem generation
[ ] Automated problem validation
[ ] Forgetting model
[ ] Intervention effectiveness model
[ ] Behavioral pattern detection
[ ] Advanced analytics
```

---

## P3 — Research-Level

```text
[ ] Bayesian learner modeling
[ ] Item Response Theory
[ ] Contextual bandits
[ ] Adaptive intervention policy
[ ] Personalized tutoring policy
[ ] Knowledge graph
[ ] ML-based behavior prediction
[ ] Longitudinal learning prediction
```

---

# 13. User Stories

## US-001 — Solve a Problem

> As a student, I want to solve programming problems inside CodeAtlas so that my learning activity can be analyzed.

### Acceptance Criteria

* Problem can be opened.
* Code can be written.
* Code can be executed.
* Tests can be run.
* Result is recorded.

---

## US-002 — Receive a Hint

> As a student, I want to ask for help without immediately receiving the complete solution.

### Acceptance Criteria

* Student can request a hint.
* Hint considers current code and problem.
* Hint level is recorded.
* Hint dependency becomes part of learner evidence.

---

## US-003 — Understand Mistakes

> As a student, I want CodeAtlas to explain what type of mistake I made.

### Acceptance Criteria

* Mistake is classified where possible.
* Classification contains confidence.
* Evidence is available internally.
* Explanation is understandable.

---

## US-004 — Personalized Practice

> As a student, I want CodeAtlas to recommend problems based on my weaknesses.

### Acceptance Criteria

* Recommendation considers learner state.
* Recommendation has a reason.
* Recommended difficulty is appropriate.
* Completing the problem updates the learner model.

---

## US-005 — Review Forgotten Concepts

> As a student, I want CodeAtlas to remind me about concepts I may be forgetting.

### Acceptance Criteria

* System tracks time since practice.
* Retrieval performance is considered.
* Review problems are generated or selected.
* Review outcome updates retention.

---

## US-006 — Track Improvement

> As a student, I want to see whether I am actually becoming better.

### Acceptance Criteria

Dashboard should show meaningful trends rather than only XP.

---

## US-007 — Independent Challenge

> As a student, I want CodeAtlas to test whether I can apply concepts to unfamiliar problems.

### Acceptance Criteria

* Problem is sufficiently novel.
* Underlying skill is related to previous learning.
* Performance is separately recorded as transfer evidence.

---

# 14. Product Metrics

CodeAtlas should distinguish between:

```text
Product Metrics
```

and:

```text
Learning Metrics
```

---

## Product Metrics

Examples:

```text
Daily active sessions
Problems attempted
Session duration
Tutor interactions
Feature usage
```

These describe product usage.

They do not prove learning.

---

## Learning Metrics

More important metrics include:

```text
Mastery improvement
Mistake reduction
Retention
Transfer performance
Hint dependency
Problem-solving time
Debugging efficiency
Independent completion rate
```

Learning metrics should dominate product decisions.

---

# 15. North Star Metric

The primary North Star Metric should be:

> **Independent Transfer Improvement**

Conceptually:

```text
Performance on unfamiliar problems
after training
-
baseline performance
```

The objective is to determine whether the student can solve new problems independently.

Supporting metrics:

```text
Mistake recurrence ↓
Hint dependency ↓
Retention ↑
Transfer ↑
Independent completion ↑
```

---

# 16. Adaptive Difficulty Model

Initial difficulty should consider:

```text
Problem difficulty
+
Learner mastery
+
Recent performance
+
Hint dependency
+
Time taken
+
Mistake frequency
```

A simple conceptual model:

```text
Effective Difficulty =
Problem Difficulty
-
Estimated Learner Competency
```

The system should target a productive challenge zone rather than:

```text
too easy
```

or:

```text
impossibly difficult
```

---

# 17. Tutor Dependency Control

A major product requirement is avoiding excessive AI dependence.

CodeAtlas should track:

```text
Hints per problem
Hint level
Time before first hint
Solution exposure
Independent completion
Post-hint performance
```

A useful trend is:

```text
Student starts:
5 hints/problem

After training:
3 hints/problem

Later:
1 hint/problem

Eventually:
0–1 hints/problem
```

This is potentially stronger evidence of improvement than simply increasing solved-problem counts.

---

# 18. Intervention Escalation

The tutor should progressively increase support.

```text
Stage 1
Ask student to inspect the problem

↓

Stage 2
Ask a diagnostic question

↓

Stage 3
Provide a small hint

↓

Stage 4
Explain relevant concept

↓

Stage 5
Guide reasoning

↓

Stage 6
Provide partial structure

↓

Stage 7
Worked solution
```

After significant assistance, CodeAtlas should ideally provide a new problem that tests whether the student actually understood the concept.

---

# 19. Learning State Update

After each meaningful problem, the system should approximately perform:

```text
1. Collect evidence
2. Classify observations
3. Update mistake state
4. Update skill evidence
5. Update behavior model
6. Update retention estimate
7. Evaluate intervention effectiveness
8. Update learner state
9. Select next objective
10. Record decision
```

This process is central to the product.

---

# 20. AI Responsibilities

The LLM may be responsible for:

```text
Natural-language explanation
Socratic dialogue
Code reasoning
Qualitative diagnosis
Problem generation
Hint generation
Reflection
Question generation
```

The LLM should NOT be the sole authority for:

```text
Mastery score
Retention score
Learning history
Security decisions
Code execution
Final correctness
```

---

# 21. Deterministic Responsibilities

Whenever possible, deterministic systems should handle:

```text
Compilation
Code execution
Test evaluation
Runtime measurement
Memory measurement
AST analysis
Event tracking
Basic complexity analysis
Database persistence
Authentication
Security boundaries
```

---

# 22. ML Responsibilities

ML may eventually handle:

```text
Skill estimation
Behavior classification
Mistake prediction
Forgetting prediction
Difficulty estimation
Intervention ranking
Learning outcome prediction
```

ML should be introduced when a sufficiently large and reliable dataset exists.

The project should not use ML merely because the product is called AI.

---

# 23. Personalization Levels

CodeAtlas should gradually personalize at multiple levels.

```text
Level 1
Topic personalization

Level 2
Sub-skill personalization

Level 3
Mistake personalization

Level 4
Behavior personalization

Level 5
Retention personalization

Level 6
Intervention personalization

Level 7
Learning-policy personalization
```

The long-term objective is Level 7.

---

# 24. Failure Handling

If AI is unavailable:

```text
IDE continues
Code execution continues
Events continue recording
Basic diagnostics continue
AI features degrade gracefully
```

If a generated problem fails validation:

```text
Reject
↓
Regenerate
↓
Validate again
↓
Fallback to verified problem
```

If learner-state confidence is low:

```text
Do not make strong diagnosis
Collect more evidence
```

---

# 25. Product Safety Principles

CodeAtlas must avoid harmful educational behavior.

The system should not:

* shame students for mistakes
* make unsupported judgments about intelligence
* create unnecessary dependency
* expose private code
* claim certainty without evidence
* manipulate students through unhealthy engagement mechanisms
* encourage cheating
* present generated explanations as guaranteed truth

---

# 26. Future Product Capabilities

Potential future features include:

```text
Personal Skill Graph
Personal Programming Fingerprint
AI Debugging Coach
Code Review Coach
Interview Preparation Mode
DSA Mastery Mode
Project-Based Learning Mode
Competitive Programming Mode
Language-Specific Learning Paths
Automatic Skill Benchmarking
Personal Learning Reports
```

These should only be implemented if they strengthen the core learning objective.

---

# 27. Product Evolution

## Phase 1

```text
IDE
+
Execution
+
Problems
+
AI Tutor
```

## Phase 2

```text
Observation
+
Mistake Detection
+
Learner Model
```

## Phase 3

```text
Adaptive Curriculum
+
Retention
+
Behavior Modeling
```

## Phase 4

```text
Transfer Evaluation
+
Problem Generation
+
Intervention Optimization
```

## Phase 5

```text
ML Learner Model
+
Adaptive Policies
+
Personal Coding Intelligence
```

---

# 28. Acceptance Definition

CodeAtlas should be considered a successful implementation of the initial product when a student can:

```text
1. Open a programming problem.
2. Write and execute code.
3. Receive meaningful feedback.
4. Have coding activity recorded.
5. Have mistakes analyzed.
6. Build a learner profile.
7. Receive personalized recommendations.
8. Practice recommended weaknesses.
9. See changes in their skill state.
10. Be evaluated on unfamiliar problems.
```

The system must demonstrate that the recommendations are actually based on the student's history.

---

# 29. Product Philosophy

The product should continuously optimize for:

```text
Understanding
    >
Completion

Independence
    >
Assistance

Transfer
    >
Memorization

Evidence
    >
Assumption

Long-term growth
    >
Short-term engagement
```

---

# 30. Final Product Requirement

The most important requirement of CodeAtlas is:

> **CodeAtlas must become better at teaching the student as it learns more about the student.**

A session today should improve the system's ability to teach the student tomorrow.

Therefore:

```text
Today's interaction
        ↓
New evidence
        ↓
Better learner model
        ↓
Better recommendation
        ↓
Better intervention
        ↓
Better learning outcome
```

That is the fundamental product loop.

---

# 31. Relationship With Other Specifications

This PRD defines **what CodeAtlas must do**.

The remaining specifications define how those requirements become an intelligent system:

```text
VISION.md
    ↓
Why are we building CodeAtlas?

Problem_Statement.md
    ↓
What problem are we solving?

PRD.md
    ↓
What must the product do?

Learning_model.md
    ↓
How do we represent the learner?

mistake_taxonomy.md
    ↓
What mistakes exist?

behavior_model.md
    ↓
How do we represent coding behavior?

Adaptive_curriculum.md
    ↓
How do we decide what to teach?

tutoring_engine.md
    ↓
How do we decide how to teach?

forgetting_and_retension.md
    ↓
How do we model knowledge decay?

problem_generator.md
    ↓
How do we create/select practice?

ai_and_ml_strategy.md
    ↓
Where should AI/ML be used?

evaluation_framework.md
    ↓
How do we know it works?

data_model.md
    ↓
How do we store the system state?

security_privacy_and_ethics.md
    ↓
How do we protect the learner?

System_Architecture.md
    ↓
How do all components work together?
```

---

# 32. Final Product Principle

> **CodeAtlas is not successful when it solves more problems for the student.**

> **CodeAtlas is successful when the student can solve more problems without it.**

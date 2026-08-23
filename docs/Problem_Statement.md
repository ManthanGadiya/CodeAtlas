# CodeAtlas — Problem Statement

## 1. Background

Programming education traditionally relies on a combination of lectures, textbooks, coding exercises, online judges, documentation, and human mentorship.

These approaches can effectively teach programming concepts, but most existing learning systems treat the learner primarily as a **problem solver** rather than as an evolving individual whose knowledge, reasoning patterns, mistakes, habits, and learning behavior can be modeled over time.

A student may solve hundreds of programming problems while still repeatedly making the same mistakes, forgetting previously learned concepts, relying excessively on hints, struggling to transfer knowledge to unfamiliar problems, or failing to understand the underlying reason for their difficulties.

The fundamental problem is therefore not a lack of available programming content.

The problem is a lack of **deep, longitudinal personalization**.

---

# 2. The Core Problem

Existing programming learning environments generally answer:

> **"What problem should the student solve?"**

and AI coding assistants generally answer:

> **"How can the student complete this coding task?"**

CodeAtlas addresses a different question:

> **"What does this particular student currently understand, where does their reasoning fail, how are they learning, what are they forgetting, and what intervention is most likely to improve their ability to solve future problems independently?"**

This requires a system that can observe the student's coding process over time and construct an evolving model of their programming competency.

---

# 3. Problem Definition

A student's final submitted program provides insufficient information to determine the student's actual level of understanding.

Consider four students who produce the same incorrect solution:

```text
Student A
→ Does not understand the algorithm.

Student B
→ Understands the algorithm but cannot implement it.

Student C
→ Understands the implementation but misunderstood the requirements.

Student D
→ Understands everything but made a careless edge-case mistake.
```

A conventional coding platform may classify all four as:

```text
Incorrect
```

A simplistic AI tutor may classify all four as:

```text
Weak in this topic
```

Neither representation accurately captures the student's underlying competency.

A useful personal coding tutor must distinguish between:

```text
Knowledge deficiency
Implementation deficiency
Reasoning deficiency
Problem interpretation deficiency
Debugging deficiency
Testing deficiency
Carelessness
Knowledge decay
Transfer failure
```

Therefore, the system must model not only **outcomes**, but also **process and longitudinal evidence**.

---

# 4. Identified Gaps

## 4.1 Lack of Longitudinal Learner Modeling

Most coding platforms track:

* solved problems
* scores
* submissions
* rankings
* difficulty

but do not construct a detailed model of how an individual programmer evolves over weeks, months, and years.

The system needs to maintain a persistent learner model containing:

* programming skills
* sub-skills
* mistakes
* behavioral patterns
* learning history
* retention
* intervention effectiveness
* problem-solving performance

---

## 4.2 Lack of Sub-Skill-Level Diagnosis

Programming topics are not atomic.

For example, "Dynamic Programming" contains multiple competencies:

```text
Dynamic Programming
│
├── Recognizing DP applicability
├── Defining state
├── Identifying transitions
├── Establishing base cases
├── Memoization
├── Tabulation
├── Space optimization
└── Complexity analysis
```

A student may be highly capable in one sub-skill and weak in another.

Therefore:

```text
Dynamic Programming = 55%
```

is insufficient.

The system must support a much more granular representation.

---

# 4.3 Lack of Root-Cause Mistake Analysis

A wrong answer does not explain why the student was wrong.

The system must identify and distinguish patterns such as:

* syntax errors
* logic errors
* off-by-one errors
* wrong algorithm selection
* complexity mistakes
* misunderstood requirements
* repeated mistakes
* copying solutions
* overengineering
* edge-case failures
* testing failures
* incorrect assumptions

More importantly, recurring mistakes should be analyzed as potential evidence of deeper weaknesses.

For example:

```text
Repeated off-by-one errors
        ↓
Possible boundary reasoning weakness
        ↓
Targeted intervention
        ↓
New evidence
        ↓
Updated learner model
```

---

# 4.4 Lack of Behavioral Understanding

A student's code alone does not capture their complete problem-solving behavior.

Important signals include:

* time to begin implementation
* time taken to solve
* number of attempts
* code revisions
* debugging sequence
* errors encountered
* tests created
* tests executed
* hints requested
* questions asked
* algorithm changes
* repeated approaches
* solution copying
* attempts to optimize prematurely

For example:

```text
Student repeatedly changes code
without forming a hypothesis
after each failure.
```

This could indicate a debugging-process weakness even if the final solution is eventually correct.

Therefore, the system must model **how the student works**, not just what they produce.

---

# 4.5 Lack of Adaptive Teaching

Traditional learning systems generally provide a predefined progression:

```text
Topic A
↓
Topic B
↓
Topic C
↓
Topic D
```

But students do not learn uniformly.

One student may have:

```text
Arrays       → Strong
Recursion    → Strong
Graphs       → Weak
DP           → Weak
Debugging    → Strong
```

Another may have completely different needs.

The curriculum should therefore be generated from the learner's current state rather than being identical for everyone.

---

# 4.6 Lack of Forgetting and Retention Modeling

A student can demonstrate mastery of a concept and later lose retrieval ability.

Existing systems often treat previous success as permanent evidence of mastery.

This creates an important distinction:

```text
Never learned
        ≠
Learned but forgotten
        ≠
Understood but cannot retrieve
        ≠
Understood but cannot transfer
```

CodeAtlas must detect evidence of knowledge decay and reintroduce concepts using appropriately timed retrieval practice.

---

# 4.7 Lack of Adaptive Tutoring Strategy

Most AI tutors primarily rely on conversational responses.

However, different students may respond differently to:

* direct explanations
* hints
* Socratic questions
* worked examples
* visual explanations
* diagnostic questions
* repeated practice
* reflection

A sophisticated tutor should therefore determine:

> **Which intervention should be used for this student, for this problem, at this moment?**

The system should eventually learn which intervention strategies are most effective for the individual learner.

---

# 4.8 Lack of Transfer-Based Evaluation

Solving a familiar problem does not necessarily demonstrate understanding.

A student may memorize:

* solution patterns
* implementation templates
* common problem structures
* previously encountered answers

without developing transferable knowledge.

Therefore, the system must evaluate performance on **unfamiliar problems that test related underlying skills**.

The key question becomes:

> **Can the student apply what they learned when the surface form of the problem changes?**

This provides a stronger measure of actual learning.

---

# 5. Proposed Solution

CodeAtlas will provide a web-based coding environment combined with an AI-powered adaptive learning system.

The student will solve programming problems inside the environment while the system collects meaningful learning evidence.

The high-level process is:

```text
Student codes
     ↓
System observes
     ↓
Code + behavior analyzed
     ↓
Evidence extracted
     ↓
Learner model updated
     ↓
Weaknesses diagnosed
     ↓
Retention estimated
     ↓
Next learning objective selected
     ↓
Problem/intervention generated
     ↓
Student practices
     ↓
Performance evaluated
     ↓
Learner model updated again
```

This creates a continuous learning loop.

---

# 6. System Inputs

The system will use multiple categories of evidence.

## 6.1 Coding Evidence

* Source code
* Code revisions
* Execution results
* Compilation errors
* Runtime errors
* Test results
* Final solutions
* Complexity characteristics

## 6.2 Behavioral Evidence

* Time taken
* Number of attempts
* Debugging sequence
* Number of revisions
* Algorithm changes
* Testing behavior
* Repeated approaches

## 6.3 Interaction Evidence

* Hints requested
* Questions asked
* Tutor interactions
* Explanations requested
* Responses to tutor questions
* Intervention effectiveness

## 6.4 Historical Evidence

* Previous performance
* Previously mastered skills
* Previous mistakes
* Time since last practice
* Previous intervention outcomes
* Historical difficulty

---

# 7. System Outputs

The system should produce several layers of personalized intelligence.

### Learner Profile

```text
Current capabilities
Weaknesses
Strengths
Behavioral patterns
Learning trends
```

### Skill Model

```text
Topic
→ Sub-skill
→ Mastery estimate
→ Confidence
→ Evidence
→ Retention
```

### Mistake Diagnosis

```text
Mistake
→ Frequency
→ Context
→ Recurrence
→ Severity
→ Potential root cause
```

### Personalized Curriculum

```text
What should be learned next?
What should be reviewed?
What should be challenged?
What should be skipped?
```

### Adaptive Tutoring

```text
Should the tutor:
→ Explain?
→ Hint?
→ Ask?
→ Challenge?
→ Demonstrate?
→ Move on?
```

---

# 8. Core Research Problem

The central research problem can be stated as:

> **How can an AI system construct and continuously update a reliable model of an individual programmer's knowledge, reasoning behavior, mistakes, retention, and learning patterns from coding activity, and use that model to select personalized interventions that improve independent problem-solving and transfer to unfamiliar programming problems?**

This problem contains several sub-problems:

### Sub-problem 1 — Observation

How can meaningful learning signals be extracted from coding activity?

### Sub-problem 2 — Representation

How should programming knowledge and competency be represented at sub-skill granularity?

### Sub-problem 3 — Diagnosis

How can recurring mistakes and behavioral patterns be mapped to underlying weaknesses?

### Sub-problem 4 — Estimation

How can the system estimate the student's current mastery and confidence?

### Sub-problem 5 — Retention

How can knowledge decay be estimated from historical performance?

### Sub-problem 6 — Adaptation

How should the system choose the next problem or intervention?

### Sub-problem 7 — Tutoring

How should the system select between explanation, hints, questioning, demonstration, and challenge?

### Sub-problem 8 — Evaluation

How can actual learning and transfer be distinguished from memorization?

---

# 9. Objectives

The project will pursue the following objectives.

## Primary Objectives

1. Build a personal web-based coding environment.
2. Capture meaningful coding and learning behavior.
3. Construct a persistent sub-skill-level learner model.
4. Develop a structured programming mistake taxonomy.
5. Detect recurring mistake patterns.
6. Model programming behavior and debugging habits.
7. Estimate skill mastery from accumulated evidence.
8. Detect potential knowledge decay.
9. Generate personalized coding practice.
10. Dynamically adapt difficulty.
11. Select appropriate tutoring interventions.
12. Evaluate learning using unfamiliar problems.
13. Measure improvement over time.
14. Maintain an explainable history of why recommendations were made.

---

# 10. Secondary Objectives

The system should eventually:

* Learn which teaching strategies work best for the student.
* Identify relationships between skills.
* Detect prerequisite weaknesses.
* Generate concept-specific interventions.
* Model learning trends.
* Recommend when to stop practicing a mastered topic.
* Detect over-reliance on AI assistance.
* Encourage independent reasoning.
* Support gamified progression.
* Adapt curriculum composition dynamically.
* Support increasingly sophisticated ML-based learner modeling.

---

# 11. Success Criteria

The project should not be considered successful merely because:

```text
The website works.
```

or:

```text
The LLM generates good questions.
```

Success should be measured through evidence of actual learning.

Important metrics include:

### Knowledge Improvement

```text
Post-test performance
-
Pre-test performance
```

### Retention

```text
Immediate performance
vs.
Delayed performance
```

### Transfer

```text
Performance on familiar problems
vs.
Performance on unseen problems
```

### Mistake Reduction

```text
Repeated mistake frequency
before vs. after intervention
```

### Independence

```text
Hint dependency
before vs. after training
```

### Problem-Solving Performance

```text
Accuracy
Time
Attempts
Debugging efficiency
```

The strongest success criterion is:

> **The student becomes increasingly capable of solving unfamiliar programming problems independently.**

---

# 12. Constraints

The system should operate under several constraints.

## 12.1 Avoid Overdependence on LLMs

The LLM should not be the sole source of truth.

Critical learner-state calculations should rely on structured evidence and deterministic or statistical components wherever possible.

---

## 12.2 Avoid Premature Diagnosis

A single mistake should not immediately cause a learner to be classified as weak.

The system should account for:

```text
Frequency
Context
Difficulty
Historical performance
Confidence
```

before making strong conclusions.

---

## 12.3 Avoid Infinite Tutoring Loops

The tutor should challenge the student but should not keep asking increasingly similar questions indefinitely.

An intervention escalation policy should eventually move toward:

```text
Hint
→ Stronger hint
→ Diagnostic explanation
→ Worked example
→ Guided solution
→ New related problem
```

---

## 12.4 Avoid Memorization-Based Progress

The system should use novel variations and unfamiliar problems to test transfer.

---

## 12.5 Protect Student Data

The system will process potentially sensitive information including:

* source code
* coding behavior
* learning history
* mistakes
* AI conversations
* performance data

Therefore, privacy and secure code execution must be treated as core architecture concerns rather than optional features.

---

# 13. Scope

The initial system will focus on **one student**.

This deliberate constraint allows the system to pursue much deeper personalization than a generalized multi-user platform.

The primary environment will be a:

> **Web-based IDE with integrated AI tutoring and learning analytics.**

The system will initially use external AI APIs such as Gemini or Groq through an abstraction layer, allowing future replacement with other models or locally hosted models.

The architecture should not permanently depend on any single AI provider.

---

# 14. Long-Term Scope

The project is intentionally designed to evolve beyond the initial implementation.

Future capabilities may include:

```text
Advanced learner modeling
        ↓
Knowledge graph
        ↓
Bayesian knowledge tracing
        ↓
Item Response Theory
        ↓
Contextual bandits
        ↓
Adaptive intervention policies
        ↓
Reinforcement learning
        ↓
Long-term personal coding intelligence
```

These are future directions rather than mandatory initial implementations.

---

# 15. Differentiation

CodeAtlas differs from existing categories in its primary objective.

| System                   | Primary Objective                               |
| ------------------------ | ----------------------------------------------- |
| Code autocomplete        | Write code faster                               |
| AI coding assistant      | Complete coding tasks                           |
| Online judge             | Evaluate solutions                              |
| Coding practice platform | Provide problems                                |
| Generic AI tutor         | Explain concepts                                |
| CodeAtlas      | **Improve the individual programmer over time** |

The system's differentiating capability is the combination of:

```text
Longitudinal observation
+
Sub-skill learner modeling
+
Behavior modeling
+
Mistake diagnosis
+
Retention modeling
+
Adaptive curriculum
+
Adaptive tutoring
+
Transfer-based evaluation
```

The combination is more important than any individual component.

---

# 16. Fundamental Hypothesis

The project is based on the following hypothesis:

> **If a programming tutor continuously models an individual's knowledge, mistakes, behavior, retention, and response to interventions, then it can provide more effective personalized training than a static curriculum or generic AI tutor, resulting in improved independent performance on unfamiliar programming problems.**

This hypothesis must be experimentally tested rather than assumed to be true.

---

# 17. Research Questions

The project should investigate questions such as:

### RQ1

Can coding activity provide sufficient evidence to estimate programming sub-skill mastery?

### RQ2

Can recurring coding mistakes be used to identify underlying conceptual or behavioral weaknesses?

### RQ3

Does sub-skill-level personalization produce better learning outcomes than topic-level personalization?

### RQ4

Can historical coding behavior provide useful signals for predicting knowledge decay?

### RQ5

Can adaptive tutoring strategies improve learning compared with a fixed tutoring strategy?

### RQ6

Does personalized curriculum selection improve performance on unfamiliar problems?

### RQ7

Can the system reduce unnecessary hint dependency over time?

### RQ8

Can an adaptive learner model accurately distinguish knowledge gaps from implementation or behavioral mistakes?

---

# 18. Final Problem Statement

> **Programming learners generate large amounts of information while coding—such as source-code revisions, errors, debugging actions, attempts, tests, questions, hints, and solution behavior—but conventional programming education systems rarely use this information to construct a persistent and granular model of the learner. As a result, students may repeatedly encounter the same weaknesses, forget previously learned concepts, receive inappropriate difficulty levels, rely excessively on assistance, and struggle to transfer knowledge to unfamiliar problems.**
>
> **CodeAtlas aims to address this problem by developing an AI-powered personal coding intelligence system that continuously observes coding and learning behavior, models programming competency at the sub-skill level, diagnoses recurring mistakes and behavioral weaknesses, estimates knowledge retention, selects adaptive tutoring interventions, and generates a personalized curriculum. The system will evaluate its effectiveness not merely through solved problems, but through measurable improvement in independent problem-solving, retention, mistake reduction, and transfer to previously unseen programming problems.**

---

## 19. Relationship With Other Documents

This document defines **why the project exists and what fundamental problem it attempts to solve**.

It should not contain detailed implementation decisions.

The following documents define the corresponding solution layers:

```text
Problem_Statement.md
        │
        ├── What problem exists?
        ├── Why does it matter?
        ├── What are the research questions?
        └── What does success mean?
                 │
                 ▼
PRD.md
        │
        └── What should the product do?
                 │
                 ▼
Learning_model.md
        │
        └── How do we represent the learner?
                 │
                 ▼
behavior_model.md
mistake_taxonomy.md
        │
        └── What evidence do we collect?
                 │
                 ▼
Adaptive_curriculum.md
tutoring_engine.md
        │
        └── How do we teach?
                 │
                 ▼
System_Architecture.md
        │
        └── How do we build it?
```

The problem statement should remain stable unless the fundamental research problem changes.

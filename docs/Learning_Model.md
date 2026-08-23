# CodeAtlas — Learning Model

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define how CodeAtlas represents, estimates, updates, and reasons about the learner's programming knowledge.

---

# 1. Purpose

The Learning Model is the core intelligence model of CodeAtlas.

Its purpose is to answer:

> **"What does CodeAtlas currently believe the student knows, does not know, is forgetting, misunderstands, or can successfully transfer to new problems?"**

The model must not represent the student using a single score.

Instead, it should maintain a multidimensional representation of programming competency.

```text
                         LEARNER
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
     Knowledge           Behavior           Retention
        │                   │                   │
        ▼                   ▼                   ▼
     Skills              Patterns          Forgetting
        │
        ▼
    Sub-skills
        │
        ▼
    Evidence
        │
        ▼
   Confidence
````

The learner model is continuously updated as new evidence becomes available.

---

# 2. Fundamental Principle

CodeAtlas must distinguish between:

```text
What happened
```

and:

```text
What we believe it means
```

For example:

```text
Observation:

Student failed binary search on a boundary case.
```

is different from:

```text
Inference:

Student has a weakness in boundary reasoning.
```

The first is evidence.

The second is a hypothesis.

This distinction is fundamental.

---

# 3. Learner Model Architecture

The learner model consists of several interconnected states.

```text
Learner Model
│
├── Skill State
│   ├── Topic
│   ├── Sub-skill
│   ├── Mastery
│   ├── Confidence
│   └── Evidence
│
├── Mistake State
│   ├── Mistake frequency
│   ├── Recurrence
│   ├── Severity
│   └── Root-cause hypotheses
│
├── Behavioral State
│   ├── Debugging
│   ├── Testing
│   ├── Assistance dependency
│   └── Problem-solving patterns
│
├── Retention State
│   ├── Last practice
│   ├── Retrieval success
│   ├── Forgetting estimate
│   └── Review priority
│
└── Intervention State
    ├── Interventions received
    ├── Effectiveness
    └── Preferred strategies
```

---

# 4. What Is a Skill?

A skill represents a specific programming capability.

The system should avoid overly broad skills such as:

```text
Programming = 72%
```

Instead, knowledge should be decomposed.

Example:

```text
Algorithms
│
├── Arrays
│
├── Searching
│   ├── Linear Search
│   └── Binary Search
│       ├── Recognition
│       ├── Implementation
│       ├── Boundary Handling
│       └── Complexity
│
├── Recursion
│   ├── Base Cases
│   ├── Recursive State
│   └── Call-Stack Reasoning
│
└── Graphs
    ├── BFS
    ├── DFS
    ├── Shortest Path
    └── Graph Representation
```

This allows CodeAtlas to identify specific weaknesses.

---

# 5. Skill Hierarchy

The learner model should support multiple levels.

```text
Domain
   ↓
Topic
   ↓
Skill
   ↓
Sub-skill
   ↓
Micro-skill
```

Example:

```text
Domain:
Algorithms

Topic:
Searching

Skill:
Binary Search

Sub-skill:
Boundary Handling

Micro-skill:
Choosing correct inclusive/exclusive interval
```

The system does not need to use all five levels immediately.

The hierarchy should become more granular as evidence becomes available.

---

# 6. Skill State

Every meaningful skill may have a state similar to:

```text
SkillState
├── skill_id
├── mastery
├── confidence
├── evidence_count
├── recent_success_rate
├── recent_failure_rate
├── retention
├── trend
├── last_practiced
├── last_success
├── last_failure
└── status
```

Example:

```text
Skill:
Binary Search — Boundary Handling

Mastery:
0.61

Confidence:
0.84

Evidence:
17 observations

Recent Success:
4 / 7

Retention:
0.72

Trend:
Improving
```

---

# 7. Mastery

Mastery represents:

> **The estimated probability that the student can successfully apply a skill under appropriate conditions.**

It is not:

```text
percentage of questions solved
```

and it is not:

```text
percentage of correct answers
```

A student might solve many easy questions but still fail when the problem changes slightly.

Therefore mastery should incorporate multiple forms of evidence.

---

# 8. Mastery Evidence

Potential evidence sources include:

```text
Correct solutions
Incorrect solutions
Problem difficulty
Independent completion
Hint usage
Mistake types
Repeated performance
Transfer performance
Delayed retrieval
Code reasoning
Debugging performance
```

Conceptually:

```text
Mastery
    ↑
    │
    ├── Correct independent solutions
    ├── Successful transfer
    ├── Delayed retrieval
    └── Consistent performance
    │
    ↓
    ├── Repeated mistakes
    ├── Heavy assistance
    ├── Transfer failures
    └── Retrieval failures
```

---

# 9. Mastery Is Not Binary

The system should not use:

```text
Mastered = TRUE
Mastered = FALSE
```

Instead:

```text
0.00 ─────────────────────────────── 1.00
 │                                    │
No evidence                         Strong evidence
```

A possible interpretation:

```text
0.00–0.20
Unknown / Very Weak

0.20–0.40
Emerging

0.40–0.60
Developing

0.60–0.75
Functional

0.75–0.90
Strong

0.90–1.00
Highly Reliable
```

These boundaries are initial design assumptions, not scientifically validated thresholds.

They must eventually be evaluated.

---

# 10. Confidence

Mastery and confidence must remain separate.

### Mastery

> How capable does the evidence suggest the student is?

### Confidence

> How certain is CodeAtlas about that estimate?

Example:

```text
Mastery: 0.80
Confidence: 0.25
```

could mean:

> The student appears capable, but there is not enough evidence to confidently establish that.

Another case:

```text
Mastery: 0.45
Confidence: 0.95
```

could mean:

> There is extensive evidence that the skill is currently weak.

---

# 11. Evidence Strength

Not every observation should influence mastery equally.

For example:

```text
Correct solution with no assistance
```

should generally provide stronger positive evidence than:

```text
Correct solution after seeing the solution.
```

Similarly:

```text
Failure on a very difficult problem
```

should not necessarily reduce mastery as much as:

```text
Failure on a problem well within the student's demonstrated ability.
```

Evidence should therefore have a strength value.

```text
Evidence
├── type
├── strength
├── confidence
├── source
├── context
└── timestamp
```

---

# 12. Evidence Types

CodeAtlas should distinguish several evidence categories.

## 12.1 Direct Evidence

Directly demonstrates competency.

Examples:

```text
Independent correct solution
Successful transfer
Correct explanation
Correct debugging reasoning
```

---

## 12.2 Indirect Evidence

Suggests competency but does not directly prove it.

Examples:

```text
Fast completion
Correct algorithm selection
Successful code optimization
```

---

## 12.3 Negative Evidence

Indicates possible weakness.

Examples:

```text
Repeated failure
Recurring mistake
Transfer failure
Retrieval failure
```

---

## 12.4 Ambiguous Evidence

Evidence that can have multiple explanations.

Example:

```text
Student submits incorrect solution.
```

Possible causes:

```text
Conceptual weakness
Implementation mistake
Requirement misunderstanding
Carelessness
```

Ambiguous evidence should not trigger aggressive learner-state updates.

---

# 13. Evidence Provenance

Every learner-state update should be traceable.

Example:

```text
Skill:
Binary Search / Boundary Handling

Current mastery:
0.58

Update:
-0.04

Reason:
Failed two boundary-focused problems.

Evidence:
E1023
E1029

Confidence:
0.91
```

This enables debugging of the learner model itself.

---

# 14. Skill Relationships

Skills should not be treated as independent variables.

Programming knowledge is interconnected.

Example:

```text
Recursion
    │
    ├──────────────┐
    ▼              ▼
DFS             Backtracking
    │
    ▼
Trees
    │
    ▼
Graphs
```

The model should eventually represent relationships such as:

```text
PREREQUISITE
RELATED_TO
DEPENDS_ON
GENERALIZES
SPECIALIZES
TRANSFER_TO
```

---

# 15. Prerequisite Reasoning

Suppose a student repeatedly fails:

```text
Dynamic Programming
```

The system should not immediately conclude:

```text
Student is weak at Dynamic Programming.
```

It should inspect prerequisites.

```text
Dynamic Programming
       │
       ├── State Representation
       │
       ├── Recurrence
       │
       └── Complexity
```

If recurrence reasoning is weak, the appropriate intervention may be:

```text
Recurrence reasoning
```

rather than:

```text
More DP problems
```

This is one of the most important purposes of the skill graph.

---

# 16. Mistake State

The learner model should separately track mistakes.

Example:

```text
MistakeState
├── mistake_type
├── frequency
├── recent_frequency
├── contexts
├── affected_skills
├── recurrence
├── severity
├── confidence
└── trend
```

Example:

```text
Mistake:
Off-by-One

Frequency:
12

Recent frequency:
5

Affected skills:
Binary Search
Sliding Window
Two Pointer

Recurrence:
High

Confidence:
0.91
```

---

# 17. Mistake-to-Skill Mapping

Mistakes should provide evidence about skills but should not map deterministically.

For example:

```text
Off-by-One Error
```

may indicate:

```text
Boundary Handling
Loop Reasoning
Indexing
Carelessness
```

Therefore:

```text
Mistake
   ↓
Candidate explanations
   ↓
Additional evidence
   ↓
Root-cause hypothesis
```

This avoids simplistic diagnosis.

---

# 18. Behavioral State

CodeAtlas should maintain a behavioral representation.

Potential dimensions:

```text
Debugging strategy
Testing strategy
Planning behavior
Hint dependency
Question behavior
Revision behavior
Algorithm switching
Optimization behavior
```

Example:

```text
Debugging Profile

Hypothesis-driven debugging:
0.42

Random modification tendency:
0.68

Test-driven debugging:
0.31

Hint dependency:
0.55
```

These values are estimates, not judgments.

---

# 19. Behavioral Patterns

The system should focus on repeated patterns.

Example:

```text
Single event:
Student changes code randomly.
```

This should not produce:

```text
Poor debugger.
```

But:

```text
Pattern:
8 sessions
+
27 failures
+
frequent unguided modifications
+
few targeted tests
```

may justify:

```text
Possible weak debugging methodology.
```

---

# 20. Retention State

Retention represents the estimated ability to retrieve a previously learned skill after a period without practice.

Example:

```text
Skill:
Binary Search

Mastery:
0.84

Retention:
0.61
```

This means:

> The student has previously demonstrated strong mastery, but current retrieval reliability may be declining.

Retention must be modeled separately from mastery.

---

# 21. Learning State Dimensions

A useful conceptual learner state is:

```text
L =
{
    mastery,
    confidence,
    retention,
    mistake_profile,
    behavior_profile,
    transfer_ability,
    assistance_dependency,
    intervention_response
}
```

The state evolves over time.

```text
L(t+1) = Update(L(t), Evidence(t))
```

The exact mathematical implementation can evolve.

---

# 22. Transfer Ability

A student may know a concept but fail to recognize when to use it.

Therefore:

```text
Concept Knowledge
```

and:

```text
Transfer Ability
```

should be represented separately.

Example:

```text
Binary Search

Implementation:
0.91

Recognition:
0.62

Transfer:
0.48
```

This reveals:

> The student can implement binary search when explicitly told to use it, but struggles to recognize when it applies.

That is a much more useful diagnosis.

---

# 23. Assistance Dependency

The system should track how much assistance the student requires.

Potential signals:

```text
Hints/problem
Hint level
Time before hint
Solution exposure
Post-hint performance
Independent performance
```

Example:

```text
Initial:
3.8 hints/problem

After training:
2.1

Later:
1.2
```

A declining assistance requirement can be evidence of increasing independence.

---

# 24. Intervention Response

CodeAtlas should record how the student responds to different interventions.

Example:

```text
Intervention:
Socratic Question

Result:
Student solved problem.

Evidence:
Positive
```

Another:

```text
Intervention:
Concept Explanation

Result:
Student still confused.

Evidence:
Weak
```

Over time the system can learn:

```text
Which interventions are effective
for which kinds of difficulties.
```

---

# 25. Intervention Effectiveness

A simple conceptual representation:

```text
InterventionEffectiveness
=
LearningOutcomeAfterIntervention
-
ExpectedOutcomeWithoutIntervention
```

Initially, CodeAtlas may not have enough data to calculate this reliably.

Therefore, the first versions should simply record:

```text
intervention
context
result
subsequent performance
```

and allow more sophisticated modeling later.

---

# 26. Learning State Update

After a meaningful learning event:

```text
New Evidence
     ↓
Evidence Validation
     ↓
Evidence Classification
     ↓
Relevant Skills Identified
     ↓
Mistake State Updated
     ↓
Behavior State Updated
     ↓
Retention State Updated
     ↓
Mastery Updated
     ↓
Confidence Updated
     ↓
Learner State Saved
```

---

# 27. Avoiding Overreaction

The learner model should not change dramatically because of one event.

Example:

```text
Previous mastery:
0.82

One difficult problem failed.

Bad:
0.82 → 0.45
```

Better:

```text
0.82 → 0.78
```

with:

```text
confidence adjustment
```

The exact update function should depend on evidence strength and context.

---

# 28. Positive Evidence

Positive evidence should be strongest when the student demonstrates independent understanding.

Example hierarchy:

```text
Strongest
│
├── Successful unfamiliar problem
├── Successful delayed retrieval
├── Successful independent problem
├── Correct explanation
├── Successful problem with small hint
├── Successful problem with strong guidance
└── Correct answer after solution exposure
Weakest
```

The exact weights should be experimentally determined.

---

# 29. Negative Evidence

Negative evidence should also be contextualized.

Example:

```text
Failure on trivial problem
```

may provide stronger evidence of a problem than:

```text
Failure on an advanced problem
```

Likewise:

```text
Repeated failure
```

should be stronger evidence than:

```text
Single failure
```

---

# 30. Difficulty-Aware Evidence

Suppose:

```text
Student mastery ≈ 0.70

Problem difficulty = 0.30

Student fails.
```

This is more informative than:

```text
Problem difficulty = 0.95

Student fails.
```

Therefore, learner updates should consider the relationship between:

```text
Learner capability
+
Problem difficulty
+
Outcome
```

---

# 31. Temporal Evidence

Recent evidence should generally have more influence than very old evidence when estimating current ability.

Example:

```text
Six months ago:
10 successful recursion problems.

Yesterday:
3 consecutive recursion failures.
```

The system should not simply count:

```text
10 success > 3 failures
```

It should consider temporal decay.

However, old evidence remains valuable for understanding:

```text
Long-term learning trajectory
```

---

# 32. Trend

Each skill should have a trend.

Possible values:

```text
STRONGLY_IMPROVING
IMPROVING
STABLE
DECLINING
STRONGLY_DECLINING
UNKNOWN
```

Trend can be derived from recent evidence.

Example:

```text
Mastery:

Week 1 → 0.42
Week 2 → 0.51
Week 3 → 0.63
Week 4 → 0.71

Trend:
IMPROVING
```

---

# 33. Skill Status

A skill can have a state such as:

```text
UNKNOWN
INTRODUCED
DEVELOPING
FUNCTIONAL
STRONG
MASTERED
AT_RISK
FORGOTTEN
```

These labels are summaries of underlying continuous estimates.

The underlying values should remain available.

---

# 34. Unknown vs Weak

This distinction is critical.

```text
Unknown
```

means:

> CodeAtlas does not have enough evidence.

Whereas:

```text
Weak
```

means:

> CodeAtlas has enough evidence to believe performance is currently insufficient.

The system must never interpret lack of evidence as evidence of weakness.

---

# 35. Mastery vs Performance

A student can perform poorly for reasons unrelated to knowledge.

For example:

```text
Poor sleep
Distraction
Ambiguous requirements
Unfamiliar environment
Temporary frustration
```

CodeAtlas should avoid treating every poor outcome as knowledge failure.

This is why learner state must remain probabilistic.

---

# 36. Learner Model Confidence

Confidence should increase when:

```text
Evidence quantity ↑
Evidence consistency ↑
Evidence diversity ↑
Transfer evidence ↑
Temporal consistency ↑
```

Confidence should decrease when:

```text
Evidence conflicts ↑
Evidence quantity ↓
Problem difficulty uncertainty ↑
Diagnosis ambiguity ↑
```

---

# 37. Learning Model Update Example

Consider a student learning binary search.

### Session 1

```text
Problem:
Basic binary search

Result:
Solved independently

Evidence:
Positive
```

Learner state:

```text
Implementation:
0.55 → 0.65
```

---

### Session 2

```text
Problem:
Binary search with duplicate values

Result:
Incorrect boundary handling
```

Evidence:

```text
Boundary handling weakness
```

---

### Session 3

```text
Problem:
Another boundary-focused problem

Result:
Same mistake
```

Now:

```text
Repeated evidence
```

Learner model:

```text
Boundary Handling:
0.48

Recurrence:
HIGH
```

---

### Session 4

Tutor provides:

```text
Socratic questioning
```

Student identifies the interval invariant.

---

### Session 5

Student solves unfamiliar boundary problem independently.

Evidence:

```text
Transfer success
```

Learner model:

```text
Boundary Handling:
0.48 → 0.67
```

This illustrates the intended learning loop.

---

# 38. Learner Model as a Graph

The long-term learner model should evolve beyond a table of scores.

Conceptually:

```text
                  Student
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Skills     Behavior    Retention
          │
     ┌────┼────┐
     ▼    ▼    ▼
  Search  DP  Graphs
     │
     ▼
Binary Search
     │
 ┌───┼──────────┐
 ▼   ▼          ▼
Recognition Implementation Boundary
```

Evidence nodes connect to these states.

```text
Mistake
   │
   ├── affects → Boundary Handling
   │
   └── observed in → Binary Search
```

This structure can eventually support graph-based reasoning.

---

# 39. Learner State Snapshot

The system should be able to create a snapshot.

Example:

```text
Learner Snapshot
──────────────────────────────

Algorithms

Arrays
    Mastery: 0.82
    Confidence: 0.91

Binary Search
    Mastery: 0.67
    Confidence: 0.84
    Retention: 0.71
    Trend: Improving

Recursion
    Mastery: 0.43
    Confidence: 0.77
    Retention: 0.52
    Trend: Declining

Graphs
    Mastery: 0.31
    Confidence: 0.62
    Retention: Unknown
    Trend: Unknown

Behavior

Debugging:
    Hypothesis-driven: 0.41

Testing:
    Edge-case testing: 0.36

Assistance Dependency:
    0.58
```

This snapshot can be used by the adaptive curriculum and tutoring engine.

---

# 40. Model Update Frequency

Not every event needs to update the complete learner model.

### High-frequency events

```text
CODE_EDITED
```

may be aggregated.

### Medium-frequency events

```text
CODE_EXECUTED
TEST_FAILED
HINT_REQUESTED
```

may produce evidence.

### High-value events

```text
PROBLEM_COMPLETED
TRANSFER_RESULT
DELAYED_RETRIEVAL
```

should trigger stronger learner-model updates.

---

# 41. Aggregation

Raw events should be aggregated into meaningful learning episodes.

Example:

```text
50 CODE_EDITED events
        ↓
1 coding episode

7 executions
        ↓
1 debugging episode

3 failed tests
        ↓
1 mistake episode
```

This prevents the learner model from being overwhelmed by low-level noise.

---

# 42. Learning Episode

A learning episode represents a meaningful unit of learning activity.

Example:

```text
LearningEpisode
├── problem_id
├── start_time
├── end_time
├── attempts
├── revisions
├── mistakes
├── hints
├── questions
├── tests
├── final_result
├── skills_involved
├── interventions
└── outcome
```

The episode becomes a higher-quality unit of evidence.

---

# 43. Model Inputs

The learner model should eventually consume:

```text
Problem metadata
Code analysis
Execution results
Test results
Mistake classifications
Behavioral signals
Tutor interactions
Historical performance
Retention intervals
Transfer results
```

---

# 44. Model Outputs

The learner model provides:

```text
Current skill estimates
Weakness candidates
Retention risks
Behavior patterns
Mistake patterns
Confidence estimates
Learning trends
Recommended learning targets
```

It does not directly generate the final problem or tutor response.

That responsibility belongs to downstream adaptive systems.

---

# 45. Separation From Curriculum

The learning model answers:

> **"What does the student currently need?"**

The curriculum engine answers:

> **"What should we do about it?"**

Example:

```text
Learner Model:
Boundary Handling is weak.

Curriculum Engine:
Schedule boundary-focused practice tomorrow.
```

This separation keeps the architecture clean.

---

# 46. Separation From Tutoring

The learning model says:

```text
Student has difficulty identifying the correct invariant.
```

The tutoring engine decides:

```text
Use a diagnostic Socratic question.
```

The learner model should not contain prompt templates or UI logic.

---

# 47. Future Mathematical Models

The initial implementation can use interpretable weighted evidence.

Later, CodeAtlas may introduce:

```text
Bayesian Knowledge Tracing
Item Response Theory
Deep Knowledge Tracing
Hidden Markov Models
Bayesian Networks
Knowledge Graphs
Contextual Bandits
Reinforcement Learning
```

These should be introduced only when sufficient evidence and evaluation infrastructure exist.

---

# 48. Recommended Evolution

## Stage 1 — Rule-Based

```text
Evidence
↓
Weighted updates
↓
Mastery estimate
```

Advantages:

* transparent
* easy to debug
* easy to validate

---

## Stage 2 — Probabilistic

```text
Evidence
↓
Bayesian estimation
↓
Mastery distribution
```

Advantages:

* uncertainty
* principled updates
* better handling of sparse evidence

---

## Stage 3 — Statistical / ML

```text
Historical evidence
↓
Learner model
↓
Predictive model
```

Potential predictions:

```text
Probability of success
Probability of forgetting
Expected intervention benefit
```

---

## Stage 4 — Adaptive Policy

Eventually:

```text
Learner State
      ↓
Candidate Actions
      ↓
Expected Learning Gain
      ↓
Policy
      ↓
Selected Intervention
```

This moves CodeAtlas from:

```text
Personalized recommendation
```

toward:

```text
Personalized learning policy.
```

---

# 49. Model Integrity Rules

The learner model must follow these rules.

### Rule 1

Never treat missing evidence as negative evidence.

### Rule 2

Never allow a single mistake to define a skill.

### Rule 3

Separate mastery from confidence.

### Rule 4

Separate mastery from retention.

### Rule 5

Separate knowledge from performance.

### Rule 6

Record evidence provenance.

### Rule 7

Preserve historical state.

### Rule 8

Allow contradictory evidence.

### Rule 9

Prefer independent demonstrations of knowledge.

### Rule 10

Use transfer performance as high-value evidence.

### Rule 11

Do not allow the LLM alone to determine learner state.

### Rule 12

Every major learner-state change should be explainable.

---

# 50. What CodeAtlas Should Eventually Know

A mature learner model should be capable of representing statements like:

```text
The student understands binary search implementation.

However:

- boundary handling is inconsistent,
- recognition of binary-search applicability is weaker,
- performance is strong on familiar problems,
- transfer performance is moderate,
- retention has recently declined,
- the student benefits from diagnostic questions,
- direct solutions increase assistance dependency,
- independent performance improves after Socratic intervention.
```

This is dramatically more useful than:

```text
Binary Search = 68%
```

---

# 51. Core Learning Loop

The final conceptual model is:

```text
              ┌──────────────────────┐
              │      Student         │
              └──────────┬───────────┘
                         │
                         ▼
                  Coding Activity
                         │
                         ▼
                    Observation
                         │
                         ▼
                      Evidence
                         │
                         ▼
                  Learner Model
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       Skills         Behavior       Retention
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                     Diagnosis
                         │
                         ▼
                 Adaptive Decision
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
          Curriculum             Tutor
              │                     │
              └──────────┬──────────┘
                         ▼
                     Intervention
                         │
                         ▼
                      Student
```

---

# 52. Final Principle

> **The learner model is not a scoreboard. It is a continuously updated hypothesis about how the student thinks, what they know, what they can apply, what they are forgetting, and what kind of intervention is most likely to help them improve.**

The quality of CodeAtlas will ultimately depend less on how sophisticated its LLM is and more on how accurately it can build and update this learner model.

A better model of the student should produce better decisions.

Better decisions should produce better learning.

And better learning should produce a student who increasingly needs CodeAtlas less.


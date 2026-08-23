# CodeAtlas — Adaptive Curriculum

> **Version:** 0.1
> **Status:** Foundational Specification
> **Project:** CodeAtlas
> **Purpose:** Define how CodeAtlas dynamically decides what the student should practice next, at what difficulty, in what format, and for what learning objective.

# 1. Purpose

A conventional coding platform typically follows:

```text
Topic
↓
Chapter
↓
Problems
↓
Next Chapter
````

CodeAtlas should work differently.

Its curriculum should be generated from the student's evolving:

```text
Knowledge
+
Mistakes
+
Behavior
+
Retention
+
Problem-solving history
+
Current goals
```

Therefore:

```text
Student State
      ↓
Curriculum Decision
      ↓
Problem / Exercise
      ↓
Student Interaction
      ↓
New Evidence
      ↓
Updated Student State
      ↓
Next Curriculum Decision
```

The curriculum is therefore **dynamic rather than predefined**.

---

# 2. Core Principle

CodeAtlas should not ask:

> "What problem comes next in the course?"

It should ask:

> **"What is the most valuable learning experience for this student right now?"**

That experience may be:

```text
A new concept
A retrieval question
A debugging exercise
A similar problem
A transfer problem
A harder problem
A simpler prerequisite problem
A reflection exercise
A code review
A timed challenge
```

---

# 3. Curriculum Objective

The curriculum optimizer should maximize:

```text
Long-Term Learning
```

rather than:

```text
Immediate Problem-Solving Success
```

A problem that the student solves instantly may provide little learning value.

A carefully selected problem that exposes a misconception and then enables correction may provide much more value.

---

# 4. Curriculum Inputs

The curriculum engine consumes evidence from:

```text
Learning Model
Mistake Taxonomy
Behavior Model
Forgetting & Retention Model
Problem Generator
Tutoring Engine
Evaluation Framework
```

Conceptually:

```text
                    Student
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Knowledge      Mistakes     Behavior
          │            │            │
          └────────────┼────────────┘
                       ▼
                 Student State
                       │
              ┌────────┴────────┐
              ▼                 ▼
         Retention          Goals
              │                 │
              └────────┬────────┘
                       ▼
              Adaptive Curriculum
                       │
                       ▼
                 Next Activity
```

---

# 5. Curriculum Units

The curriculum should not consist exclusively of full programming problems.

It should contain multiple activity types.

```text
C01 — Concept Retrieval
C02 — Micro Exercise
C03 — Debugging Exercise
C04 — Guided Problem
C05 — Standard Problem
C06 — Transfer Problem
C07 — Challenge Problem
C08 — Code Review
C09 — Complexity Exercise
C10 — Test Design Exercise
C11 — Reflection Exercise
C12 — Delayed Retrieval
```

This allows CodeAtlas to target different weaknesses.

---

# 6. Activity Type Selection

For every curriculum decision, CodeAtlas chooses:

```text
Activity Type
+
Topic
+
Skill
+
Difficulty
+
Novelty
+
Support Level
+
Expected Learning Objective
```

Example:

```text
Activity:
Debugging Exercise

Skill:
Binary Search Boundaries

Difficulty:
Medium

Objective:
Fix off-by-one errors independently

Support:
Minimal hint
```

---

# 7. Skill Graph

The curriculum should operate on a graph rather than a flat topic list.

Example:

```text
Programming
│
├── Fundamentals
│   ├── Variables
│   ├── Conditions
│   └── Loops
│
├── Data Structures
│   ├── Arrays
│   ├── Hash Maps
│   ├── Stacks
│   └── Queues
│
├── Algorithms
│   ├── Searching
│   │   └── Binary Search
│   ├── Sorting
│   ├── Graph Algorithms
│   └── Dynamic Programming
│
└── Problem Solving
    ├── Decomposition
    ├── Complexity
    ├── Debugging
    └── Testing
```

Skills should have prerequisite relationships.

---

# 8. Prerequisite Graph

Example:

```text
Arrays
  ↓
Two Pointer
  ↓
Sliding Window
  ↓
Advanced Sliding Window
```

Another:

```text
Recursion
  ↓
Backtracking
  ↓
Tree Search
  ↓
Advanced Graph Search
```

If a student struggles with:

```text
Sliding Window
```

CodeAtlas should investigate whether the actual problem is:

```text
Array indexing
Two pointers
Loop invariants
```

rather than simply assigning more sliding-window problems.

---

# 9. Skill State

Every important skill should have a state.

Conceptually:

```text
SkillState
{
    mastery,
    confidence,
    retention,
    recognition,
    transfer,
    implementation,
    prerequisites,
    evidence,
    trend
}
```

Example:

```text
Binary Search

Mastery:
0.78

Implementation:
0.91

Recognition:
0.52

Transfer:
0.48

Retention:
0.84
```

This tells CodeAtlas something important:

> The student can implement binary search but struggles to recognize when it should be used.

---

# 10. Sub-Skill Adaptation

CodeAtlas should avoid assigning:

```text
"Binary Search Practice"
```

as a single category.

Instead:

```text
Binary Search
├── Basic Implementation
├── Boundary Handling
├── Search Space Reasoning
├── Complexity
├── Recognition
├── Answer-Space Search
└── Transfer
```

This is one of the most important design principles of CodeAtlas.

---

# 11. Curriculum Decision Types

CodeAtlas should primarily make five types of decisions.

```text
A — Reinforce
B — Repair
C — Extend
D — Retrieve
E — Transfer
```

---

# 12. A — Reinforce

Used when:

```text
Skill is known
+
Retention is acceptable
+
Student benefits from additional practice
```

Example:

```text
Binary Search:
Mastery = 0.78
Retention = 0.81
Transfer = 0.72
```

Action:

```text
Give moderately varied practice.
```

---

# 13. B — Repair

Used when:

```text
A significant weakness or misconception exists.
```

Example:

```text
Off-by-one errors
+
High recurrence
+
Low boundary reasoning
```

Action:

```text
Targeted boundary exercise.
```

The system should repair the underlying skill rather than repeatedly exposing the student to full problems.

---

# 14. C — Extend

Used when:

```text
Skill is strong enough
+
Prerequisites are stable
```

Action:

```text
Increase difficulty
OR
introduce a deeper variant.
```

Example:

```text
Binary Search
↓
Search on answer space
```

---

# 15. D — Retrieve

Used when:

```text
Skill was previously mastered
+
Retention probability is declining.
```

Action:

```text
Short retrieval exercise.
```

The goal is to prevent forgetting without consuming too much curriculum time.

---

# 16. E — Transfer

Used when:

```text
Student performs well in familiar contexts
but struggles in unfamiliar contexts.
```

Example:

```text
Student solves:
Binary search on sorted arrays.

Fails:
Minimum feasible answer problem.
```

Action:

```text
Transfer problem.
```

---

# 17. Curriculum Decision Hierarchy

When multiple interventions are possible, CodeAtlas should roughly prioritize:

```text
Critical prerequisite failure
        ↓
Major misconception
        ↓
Persistent repeated mistake
        ↓
Retention risk
        ↓
Transfer weakness
        ↓
Skill reinforcement
        ↓
Difficulty extension
```

This is a starting policy, not a permanent formula.

---

# 18. Difficulty Model

Difficulty should be multidimensional.

A problem may be difficult because of:

```text
Concept Difficulty
Reasoning Difficulty
Implementation Difficulty
Debugging Difficulty
Problem Novelty
Time Complexity
Code Complexity
```

Therefore:

```text
Difficulty ≠ Number of Lines
```

---

# 19. Difficulty Levels

Initial conceptual levels:

```text
L0 — Familiar
L1 — Easy
L2 — Moderate
L3 — Challenging
L4 — Advanced
L5 — Expert
```

These levels should be relative to the student's current capability.

---

# 20. Adaptive Difficulty

If a student repeatedly succeeds:

```text
L2
L2
L2
```

CodeAtlas may try:

```text
L3
```

If the student struggles heavily:

```text
L3
↓
L3
↓
L3
```

the system should not blindly continue increasing difficulty.

It should diagnose why.

---

# 21. Difficulty vs Weakness

Suppose:

```text
Student fails a hard problem.
```

Possible reasons:

```text
A. Problem genuinely too difficult.
B. Missing prerequisite.
C. Misconception.
D. Poor problem recognition.
E. Weak debugging.
F. Weak retention.
```

Therefore:

> **Failure does not automatically mean difficulty should decrease.**

Diagnosis comes first.

---

# 22. Challenge Zone

CodeAtlas should maintain a target zone where the student is:

```text
challenged
but
not consistently overwhelmed.
```

Conceptually:

```text
Too Easy
────────────
Low learning value

Optimal Challenge
──────────────────
High learning value

Too Hard
────────────
Frustration / guessing / dependency
```

The optimal region should move as the student improves.

---

# 23. Avoiding the "Same Question Trap"

CodeAtlas must not keep giving the exact same problem until the student solves it.

Instead:

```text
Attempt 1:
Original problem

Failure
↓
Targeted intervention

Attempt 2:
Simplified analogous problem

Success
↓
Attempt 3:
Related problem

Success
↓
Attempt 4:
Original concept in a new context
```

This creates learning rather than brute-force repetition.

---

# 24. Threshold-Based Repetition

If the student has not demonstrated sufficient understanding, CodeAtlas should repeat the underlying concept.

However:

```text
Repeat Concept
```

does not mean:

```text
Repeat Exact Problem
```

The system should vary:

```text
context
input
representation
surface wording
difficulty
constraints
```

---

# 25. Mastery Threshold

A skill should not be considered mastered after one successful problem.

A conceptual mastery threshold may require evidence across:

```text
Independent Success
+
Consistency
+
Recognition
+
Transfer
+
Delayed Retrieval
```

Example:

```text
Basic mastery:
3 successful problems

Strong mastery:
success across varied contexts

Robust mastery:
delayed retrieval + transfer
```

Exact thresholds should be validated experimentally.

---

# 26. Mastery Bands

Possible states:

```text
0.00–0.20  Unknown
0.20–0.40  Emerging
0.40–0.60  Developing
0.60–0.75  Functional
0.75–0.90  Strong
0.90–1.00  Robust
```

These values are provisional.

They should not be treated as scientifically validated boundaries.

---

# 27. Mastery Is Multidimensional

Avoid:

```text
Binary Search = 82%
```

Instead:

```text
Binary Search

Implementation      0.91
Recognition         0.54
Boundary Reasoning  0.63
Complexity          0.86
Transfer            0.48
Retention           0.81
```

This gives the curriculum engine something actionable.

---

# 28. Problem Selection

A candidate problem should be evaluated against:

```text
Target Skill
Prerequisites
Difficulty
Novelty
Mistake Relevance
Retention Need
Transfer Need
Behavioral Objective
Recent Exposure
```

---

# 29. Candidate Problem Pool

The system may generate or retrieve many candidates:

```text
P1
P2
P3
...
P100
```

The curriculum engine ranks them.

Conceptually:

```text
Candidate Problems
        ↓
Filter invalid candidates
        ↓
Score educational relevance
        ↓
Apply diversity constraints
        ↓
Select best candidate
```

---

# 30. Candidate Scoring

A conceptual score:

```text
Candidate Score =
    Skill Relevance
  + Learning Need
  + Appropriate Difficulty
  + Novelty
  + Transfer Value
  + Retention Value
  + Behavioral Value
  - Repetition Penalty
  - Frustration Risk
```

The exact implementation should evolve through evaluation.

---

# 31. Diversity Constraint

CodeAtlas should avoid:

```text
10 nearly identical binary-search problems.
```

Instead:

```text
Binary Search
├── Sorted array
├── First/last occurrence
├── Rotated array
├── Search on answer
├── Feasibility problem
└── Real-world interpretation
```

Diversity helps determine whether the student truly understands the concept.

---

# 32. Spaced Practice

Previously learned skills should periodically return.

Example:

```text
Day 1:
Binary Search

Day 3:
Binary Search retrieval

Day 8:
Binary Search transfer

Day 20:
Binary Search advanced application
```

This prevents:

```text
"I knew this last month."
```

from becoming:

```text
"I cannot recall it now."
```

---

# 33. Interleaving

The curriculum should sometimes mix concepts.

Example:

```text
Problem 1:
Hash Map

Problem 2:
Binary Search

Problem 3:
Two Pointer

Problem 4:
Hash Map

Problem 5:
Binary Search
```

This forces recognition.

If every binary-search problem appears consecutively, the student may simply learn:

```text
"Next problem = binary search."
```

That is not genuine algorithm recognition.

---

# 34. Recognition Training

To improve algorithm recognition, CodeAtlas may present:

```text
Problem statement
```

and ask:

> "Which approach is most promising and why?"

before allowing implementation.

This separates:

```text
Recognition
```

from:

```text
Implementation.
```

---

# 35. Transfer Curriculum

Transfer problems should modify the surface context while preserving the underlying reasoning.

Example:

```text
Known:
Binary search on sorted array.

Transfer:
Find minimum feasible capacity.

Advanced transfer:
Optimization problem with monotonic feasibility.
```

The student must recognize the hidden structure.

---

# 36. Novelty Control

Novelty should be controlled.

Too little:

```text
memorization
```

Too much:

```text
cognitive overload
```

The curriculum should gradually increase novelty.

---

# 37. Retrieval Curriculum

Retrieval activities should be short.

Examples:

```text
"Write binary search from memory."

"What invariant does this loop maintain?"

"Give the time complexity."

"When should BFS be preferred over DFS?"
```

Retrieval should not always require a full coding problem.

---

# 38. Debugging Curriculum

When debugging is the target skill, the student may receive intentionally broken code.

Example:

```text
Correct algorithm
+
One subtle bug
```

The task:

```text
Find
Explain
Fix
Test
```

This isolates debugging ability from algorithm invention.

---

# 39. Testing Curriculum

The student may receive:

```text
Correct solution
```

and be asked:

> "Write the smallest set of tests that could break this implementation."

This directly trains test reasoning.

---

# 40. Complexity Curriculum

The system may present:

```text
Three correct implementations
```

and ask:

```text
Which scales best?
Why?
What are the time/space complexities?
```

This develops trade-off reasoning.

---

# 41. Behavior Curriculum

Some activities should target programming behavior.

Example:

```text
Detected:
Random debugging
```

CodeAtlas gives:

```text
Broken program
```

with instructions:

```text
Before changing the code:
1. State your hypothesis.
2. Create one test.
3. Predict the result.
```

The goal is behavioral change.

---

# 42. Metacognitive Curriculum

CodeAtlas should occasionally ask:

```text
"What caused your previous mistake?"

"What signal did you miss?"

"What would you do differently next time?"

"How could you detect this bug earlier?"
```

These should be used selectively.

---

# 43. Goal-Aware Curriculum

The curriculum should eventually support user goals.

Examples:

```text
DSA Interview Preparation
Competitive Programming
Backend Development
Machine Learning
Systems Programming
College Coursework
General Programming
```

Goal changes the curriculum priorities.

---

# 44. Goal Conflict

If the student's personal goal is:

```text
Backend Development
```

but CodeAtlas detects:

```text
Weak recursion
```

it should not necessarily spend 40% of the curriculum on recursion.

Instead:

```text
Goal relevance
+
Prerequisite importance
+
Learning value
```

should determine allocation.

---

# 45. Curriculum Allocation

A conceptual weekly allocation:

```text
40% — Current Weakness Repair
25% — New / Extending Skills
15% — Retrieval / Retention
10% — Transfer
10% — Behavioral / Debugging Practice
```

These are starting recommendations, not fixed rules.

The system should dynamically adjust them.

---

# 46. Recommended Initial Allocation

For the first version:

```text
35% Weakness Repair
25% Skill Development
15% Retention
15% Transfer
10% Behavioral Training
```

This provides enough emphasis on weaknesses without trapping the learner in remediation.

---

# 47. Avoiding Weakness Overfitting

Suppose:

```text
Student repeatedly makes off-by-one errors.
```

CodeAtlas should not generate:

```text
30 boundary problems.
```

Instead:

```text
5 targeted exercises
+
2 transfer exercises
+
normal curriculum
+
delayed retrieval
```

The student should continue progressing.

---

# 48. Curriculum Recovery

If a student performs poorly for several consecutive activities:

```text
Do not immediately conclude:
"Student became worse."
```

Investigate:

```text
recent difficulty increase
topic transition
retention issue
misconception
behavior change
problem quality
```

Then adjust.

---

# 49. Curriculum Escalation

A skill may move through:

```text
Introduction
↓
Guided Practice
↓
Independent Practice
↓
Variation
↓
Transfer
↓
Advanced Application
```

Each stage requires evidence.

---

# 50. Curriculum Regression

If a previously strong skill deteriorates:

```text
Advanced Application
↓
Failure
↓
Delayed Retrieval
↓
Foundational Retrieval
↓
Rebuild
↓
Transfer
```

Regression should be temporary and targeted.

---

# 51. Avoiding Permanent Regression

The curriculum should not permanently downgrade the student because of one failure.

Example:

```text
Student has 20 successful binary-search problems.

Then fails one unusual problem.
```

Do not conclude:

```text
Binary Search Mastery = 0.3
```

Instead:

```text
Investigate failure
↓
Determine whether it is:
Novelty
Transfer
Specific misconception
```

---

# 52. Confidence-Aware Curriculum

When evidence is uncertain:

```text
High-confidence weakness
```

→ direct intervention.

When:

```text
Low-confidence weakness
```

→ diagnostic activity.

Example:

```text
Possible Binary Search Misconception
confidence = 0.38
```

CodeAtlas should ask a diagnostic question before restructuring the curriculum.

---

# 53. Curriculum as Experimentation

The system should treat interventions as experiments.

Example:

```text
Hypothesis:
Student struggles with boundary reasoning.

Intervention:
Boundary-focused exercise.

Observation:
Performance improves.

Update:
Hypothesis confidence increases.
```

This creates a closed learning loop.

---

# 54. Curriculum Policy

The curriculum policy maps:

```text
Student State
```

to:

```text
Next Activity
```

Conceptually:

```text
π(StudentState) → Activity
```

This is intentionally compatible with future ML/RL-based approaches.

---

# 55. Rule-Based First Version

Version 1 should use interpretable rules.

Example:

```text
IF
    mistake.recurrence == HIGH
AND
    mistake.confidence > 0.80
AND
    skill.mastery < 0.65
THEN
    choose targeted repair exercise
```

Another:

```text
IF
    mastery > 0.80
AND
    retention < 0.60
THEN
    choose retrieval activity
```

Another:

```text
IF
    implementation > 0.80
AND
    recognition < 0.60
THEN
    choose recognition exercise
```

---

# 56. Why Rule-Based First?

Because CodeAtlas needs:

```text
interpretability
debuggability
predictability
```

before introducing sophisticated adaptive algorithms.

The system should first prove:

```text
Adaptive curriculum actually improves learning.
```

Then more advanced methods can be introduced.

---

# 57. Future ML Curriculum Engine

Later versions may use:

```text
Contextual Bandits
Bayesian Knowledge Tracing
Deep Knowledge Tracing
Item Response Theory
Reinforcement Learning
Multi-Armed Bandits
```

These should be introduced only after enough learner interaction data exists.

---

# 58. Multi-Armed Bandit Possibility

Suppose CodeAtlas is uncertain whether the student benefits more from:

```text
A — More coding problems
B — Retrieval practice
C — Debugging exercises
D — Concept explanation
```

The system can experiment with interventions and observe:

```text
learning gain
retention
transfer
engagement
```

This can eventually become a contextual bandit problem.

---

# 59. Reward Signal

A future curriculum optimizer should not use:

```text
Immediate correctness
```

as its only reward.

Potential reward components:

```text
Immediate Success
Delayed Retention
Transfer Success
Reduced Hint Dependency
Reduced Repeated Mistakes
Improved Debugging
Improved Problem Recognition
```

Long-term learning should dominate.

---

# 60. Curriculum Feedback

After each activity:

```text
Activity Outcome
      ↓
Learning Evidence
      ↓
Update Student State
      ↓
Recalculate Needs
      ↓
Choose Next Activity
```

This means the curriculum can change after every meaningful interaction.

---

# 61. Daily Curriculum

The user may receive a daily plan such as:

```text
Today's CodeAtlas Session

1. Retrieval — Binary Search
   5 minutes

2. Weakness Repair — Boundary Reasoning
   15 minutes

3. Standard Problem — Two Pointer
   20 minutes

4. Transfer — Search on Answer
   20 minutes

5. Debugging Exercise
   10 minutes

6. Reflection
   5 minutes
```

The exact plan should adapt to the student's state.

---

# 62. Session Length

CodeAtlas should not assume a fixed session length.

Possible modes:

```text
Quick
Normal
Deep Practice
Exam Mode
```

The curriculum should fit the available session rather than forcing unnecessary work.

---

# 63. Session Interruption

If a session ends early:

```text
Current state
```

should be preserved.

The next session should continue intelligently.

It should not simply restart the same problem.

---

# 64. Curriculum Memory

CodeAtlas should remember:

```text
recent problems
recent concepts
recent mistakes
recent interventions
recent successes
recent failures
```

This prevents repetitive curriculum generation.

---

# 65. Repetition Penalty

If the student recently solved several highly similar problems:

```text
Similarity ↑
```

then:

```text
Candidate Score ↓
```

unless repetition is intentionally required for remediation.

---

# 66. Difficulty Adjustment

Difficulty may be adjusted based on:

```text
recent success rate
mistake severity
hint usage
independence
time
transfer performance
```

But no single metric should dominate.

---

# 67. Example Adaptive Sequence

Initial state:

```text
Binary Search Implementation:
Strong

Recognition:
Weak

Transfer:
Weak
```

Curriculum:

```text
1. Algorithm selection question
2. Familiar binary-search problem
3. Interleaved non-binary-search problem
4. Search-on-answer transfer problem
5. Delayed retrieval
```

This is better than:

```text
5 binary-search implementations.
```

---

# 68. Example Weakness Repair

Detected:

```text
Repeated Off-by-One
```

Curriculum:

```text
1. Identify boundary bug
2. Explain boundary invariant
3. Fix tiny code snippet
4. Solve simple problem
5. Solve unrelated boundary problem
6. Delayed retrieval
```

The progression moves from:

```text
Recognition
→
Understanding
→
Implementation
→
Transfer
→
Retention
```

---

# 69. Curriculum Stopping Conditions

A weakness intervention should stop when:

```text
Target skill reaches threshold
+
independent success
+
varied success
+
reasonable retention evidence
```

Do not continue endlessly.

---

# 70. Curriculum Escalation Trigger

Increase difficulty when:

```text
success is stable
+
hint dependency is low
+
mistake recurrence is low
+
transfer is acceptable
```

---

# 71. Curriculum De-escalation Trigger

Reduce difficulty or provide scaffolding when:

```text
repeated failure
+
high confusion
+
low prerequisite mastery
+
high assistance dependency
```

But first diagnose the cause.

---

# 72. Scaffolding

Scaffolding may include:

```text
Question
↓
Hint
↓
Concept reminder
↓
Partial structure
↓
Pseudocode
↓
Partial implementation
```

The system should use the smallest effective intervention.

---

# 73. Minimal Effective Intervention

Core principle:

> **Give the least assistance required to produce meaningful progress.**

Example:

```text
Student forgot a syntax detail.
```

Do not explain the entire algorithm.

Instead:

```text
Provide syntax reminder.
```

---

# 74. Curriculum Fairness

CodeAtlas should not make assumptions such as:

```text
slow student = weak student
many attempts = poor student
many questions = dependent student
AI usage = cheating
```

Curriculum decisions must be evidence-based.

---

# 75. Curriculum Explainability

The student should eventually be able to ask:

> "Why did CodeAtlas give me this problem?"

Example answer:

```text
You received this problem because:

- You solved the basic version of binary search reliably.
- You still struggle to recognize when binary search applies.
- You have not practiced answer-space search recently.
- This problem targets that exact gap.
```

This creates trust.

---

# 76. Curriculum Transparency

The student should be able to see:

```text
Current Focus
Why It Matters
Evidence
Next Goal
Progress
```

Example:

```text
Current Focus:
Boundary Reasoning

Evidence:
5 boundary-related mistakes in the last 12 problems.

Goal:
Solve 4 varied boundary problems independently.

Next:
One short debugging exercise.
```

---

# 77. Curriculum Personalization

Two students solving the same course should eventually receive different paths.

Student A:

```text
Strong algorithms
Weak debugging
```

Student B:

```text
Strong debugging
Weak algorithms
```

Their curricula should diverge.

That is the point of CodeAtlas.

---

# 78. Curriculum Convergence

Personalization does not mean infinite divergence.

Students may eventually converge on:

```text
core competencies
```

while taking different routes.

Example:

```text
Student A:
Debugging → Arrays → Graphs

Student B:
Arrays → Graphs → Debugging
```

Both may reach:

```text
Robust Programming Skill
```

---

# 79. Long-Term Curriculum

The curriculum should operate at multiple timescales.

```text
Per Attempt
↓
Per Session
↓
Daily
↓
Weekly
↓
Monthly
```

### Per Attempt

Immediate adaptation.

### Per Session

Balance topics and activities.

### Daily

Target current weaknesses.

### Weekly

Review trends.

### Monthly

Evaluate broader skill development.

---

# 80. Curriculum Evolution

A student's curriculum should evolve:

```text
Beginner
↓
Foundation Building
↓
Independent Problem Solving
↓
Pattern Recognition
↓
Transfer
↓
Advanced Reasoning
↓
Expert Practice
```

The system should not lock the learner into a static level.

---

# 81. Long-Term Objective

The curriculum should gradually shift from:

```text
CodeAtlas tells student what to do.
```

toward:

```text
Student understands what they need to practice.
```

Eventually:

```text
CodeAtlas
    ↓
Develops metacognition
    ↓
Student self-diagnoses
    ↓
Student chooses practice
    ↓
CodeAtlas validates / adjusts
```

This is an important long-term objective.

---

# 82. Ultimate Curriculum Loop

```text
                 ┌──────────────────────┐
                 │    Student State     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Identify Learning  │
                 │        Need         │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Select Activity Type │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Select / Generate    │
                 │      Problem        │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Student Attempts     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Collect Evidence     │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Update Learner Model │
                 └──────────┬───────────┘
                            │
                            └───────────────┐
                                            │
                                            ▼
                                  Next Curriculum
```

---

# 83. Final Principles

### Principle 1

The curriculum is generated from evidence.

### Principle 2

One failure should not define the learner.

### Principle 3

Weaknesses should be repaired without trapping the student in repetition.

### Principle 4

Recognition and transfer deserve separate practice.

### Principle 5

Retention must be continuously tested.

### Principle 6

Behavior is part of learning.

### Principle 7

Difficulty should adapt to the learner.

### Principle 8

The smallest effective intervention should be preferred.

### Principle 9

Curriculum decisions should remain explainable.

### Principle 10

Long-term independence is more important than short-term correctness.

---

# 84. Final Vision

The ultimate CodeAtlas curriculum should feel less like:

```text
"Here are today's 5 coding questions."
```

and more like:

```text
"Based on how you have been solving problems,
here is exactly what you need next."

You are strong at implementation.

You are weaker at recognizing when an algorithm applies.

You have also started forgetting graph traversal details.

So today's session will:

1. Retrieve BFS from memory.
2. Test algorithm recognition.
3. Give you an unfamiliar graph problem.
4. Observe your reasoning.
5. Revisit the concept only if necessary.
6. Finish with a delayed retrieval task.

Tomorrow's curriculum will depend on what happens today.
```

That is the core of an **adaptive coding curriculum**.
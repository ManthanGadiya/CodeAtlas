# CodeAtlas — Tutoring Engine

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define how CodeAtlas interacts with the student during coding, debugging, learning, questioning, and practice.

---

# 1. Purpose

The Tutoring Engine is the **interaction and intervention layer** of CodeAtlas.

It sits between:

```text
Student
   ↕
Tutoring Engine
   ↕
Learning Model
Behavior Model
Mistake Taxonomy
Adaptive Curriculum
Problem Generator
Retention Model
AI Models
````

Its job is not simply to answer questions.

Its primary objective is:

> **Help the student become capable of solving the problem independently.**

Therefore, CodeAtlas should not optimize for:

```text
Fastest answer
Most detailed explanation
Maximum code generation
Maximum student satisfaction
```

Instead, it should optimize for:

```text
Learning
+
Understanding
+
Independence
+
Transfer
+
Retention
```

---

# 2. Core Philosophy

A conventional coding assistant behaves approximately like:

```text
Student:
"My code doesn't work."

AI:
"Here is the corrected code."
```

CodeAtlas should behave more like:

```text
Student:
"My code doesn't work."

CodeAtlas:
"What did you expect this test to return?"

Student:
"7."

CodeAtlas:
"What does it actually return?"

Student:
"6."

CodeAtlas:
"Which part of your algorithm is responsible for determining
that value?"

Student:
"The loop boundary."

CodeAtlas:
"Good. Before changing it, what do you think the boundary
should include?"
```

The tutor guides the student's reasoning rather than replacing it.

---

# 3. Tutoring Objective

The tutoring engine should maximize:

```text
Independent Progress
```

subject to:

```text
Student Understanding
Student Frustration
Problem Difficulty
Time
Learning Objective
```

Conceptually:

```text
Tutor Quality =
Learning Gain
+
Independence Gain
+
Retention Gain
+
Behavior Improvement
-
Unnecessary Assistance
```

---

# 4. Tutoring Architecture

```text
                    Student
                       │
                       ▼
               Interaction Layer
                       │
                       ▼
                Event Collector
                       │
                       ▼
               Context Builder
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Learning Model  Behavior Model  Mistake Model
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 Tutor State
                       │
                       ▼
              Intervention Selector
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Question      Hint        Explanation
          │            │            │
          └────────────┼────────────┘
                       ▼
                 AI Generation
                       │
                       ▼
                    Student
```

---

# 5. Tutor Modes

The tutoring engine should support different modes.

```text
T01 — Socratic Tutor
T02 — Hint Tutor
T03 — Debugging Coach
T04 — Concept Teacher
T05 — Code Reviewer
T06 — Test Coach
T07 — Complexity Coach
T08 — Reflection Coach
T09 — Challenge Coach
T10 — Emergency Explanation
```

The engine chooses the mode dynamically.

---

# 6. Socratic Tutor

The Socratic mode uses questions to make the student reason.

Example:

```text
Student:
"My binary search doesn't work."

Tutor:

What should happen when nums[mid] is greater than target?

What does your current code do in that case?

Which part of the search space should remain?
```

The goal is:

```text
Question
↓
Student reasoning
↓
Discovery
```

rather than:

```text
Question
↓
Student waits
↓
Tutor answers everything
```

---

# 7. Hint Tutor

Hints should reveal progressively more information.

The system should not immediately expose the solution.

Example:

```text
H0:
No hint

H1:
"Look at how the left boundary changes."

H2:
"Ask whether the current midpoint has already been eliminated."

H3:
"Your left boundary may need to move beyond mid."

H4:
"Consider setting left = mid + 1."

H5:
Partial implementation

H6:
Complete solution
```

---

# 8. Hint Escalation

The default escalation should be:

```text
Minimal Hint
      ↓
Question
      ↓
Conceptual Hint
      ↓
Specific Hint
      ↓
Partial Solution
      ↓
Full Solution
```

The engine should skip levels when necessary.

---

# 9. Minimum Effective Help

Core principle:

> **Give the smallest intervention that is likely to restore productive progress.**

Example:

```text
Student forgot Python syntax.

Bad:
Explain the entire algorithm.

Good:
"Python uses `dict.get(key, default)` here."
```

---

# 10. When to Intervene

CodeAtlas should not interrupt every mistake.

Intervention may be triggered by:

```text
Repeated failure
Long unproductive loop
Repeated identical edits
Misconception
Critical misunderstanding
Early solution dependency
Request for help
Behavioral pattern
```

---

# 11. Passive Observation

The tutor should sometimes remain silent.

Example:

```text
Student:
Makes a small syntax error.

Student:
Reads error.

Student:
Fixes it independently.
```

CodeAtlas should record:

```text
Independent Recovery
```

and avoid unnecessary intervention.

---

# 12. Intervention Threshold

Conceptually:

```text
Intervene when:

Expected benefit of intervention
>
Expected learning value of independent struggle
```

This is one of the central decisions in CodeAtlas.

---

# 13. Productive Struggle

CodeAtlas should allow students to struggle.

A certain amount of difficulty is useful because it creates:

```text
Retrieval effort
Hypothesis formation
Error recognition
Self-correction
Metacognition
```

Therefore:

```text
Difficulty ≠ Failure
```

---

# 14. Unproductive Struggle

Intervene when the student is stuck in a loop such as:

```text
Attempt
↓
Same error
↓
Same modification
↓
Same error
↓
Same modification
```

This is different from productive exploration.

---

# 15. Stuck Detection

Potential signals:

```text
time without meaningful progress
repeated executions
repeated identical errors
repeated code changes
no strategy change
rapid hint requests
```

No single signal should trigger intervention alone.

---

# 16. Stuck State

Conceptually:

```text
StuckScore =
    TimeFactor
  + RepetitionFactor
  + FailureFactor
  + StrategyFixation
  - ProgressEvidence
```

The exact formula should be calibrated experimentally.

---

# 17. Progress Detection

Progress can include:

```text
New hypothesis
New test
Reduced search space
Improved complexity
Corrected misconception
New strategy
Successful partial result
```

A student may make no code progress while making significant reasoning progress.

The tutor should recognize that.

---

# 18. Context Builder

Before responding, the tutor should construct a context.

Example:

```text
TutorContext
{
    problem,
    requirements,
    constraints,
    current_code,
    code_history,
    recent_tests,
    execution_results,
    compiler_errors,
    previous_hints,
    student_questions,
    known_mistakes,
    skill_state,
    behavior_state,
    current_learning_goal,
    session_history
}
```

The AI should not receive arbitrary historical data.

Only relevant context should be included.

---

# 19. Current State vs Historical State

The tutor should distinguish:

```text
Current Problem
```

from:

```text
Long-Term Student Profile
```

Example:

```text
Current:
Student has an off-by-one error.

Historical:
Student has repeatedly struggled with boundaries.
```

The second makes the intervention more targeted.

---

# 20. Personalized Intervention

Instead of:

```text
"Check your loop."
```

CodeAtlas may say:

```text
"You have made boundary mistakes in several recent problems.

Before changing this loop, tell me:
What values should `i` be allowed to take?"
```

This directly targets the student's known weakness.

---

# 21. Tutoring Strategy Selection

The engine should select an intervention based on:

```text
Learning Goal
Student State
Current Error
Behavior
Previous Interventions
Hint History
Difficulty
Frustration Risk
```

Example:

```text
Weak concept
+
Low confidence
+
No previous explanation
→ Concept explanation

Known concept
+
Debugging error
→ Socratic debugging

Repeated mistake
→ Metacognitive intervention

Strong skill
+
Simple bug
→ Minimal hint
```

---

# 22. Intervention Types

The engine should support:

```text
QUESTION
HINT
EXPLANATION
COUNTEREXAMPLE
ANALOGY
VISUALIZATION
TRACE
PARTIAL_CODE
TEST_CASE
PSEUDOCODE
SOLUTION
REFLECTION
```

---

# 23. Question Intervention

Use when the student can likely discover the answer.

Example:

```text
"Which condition causes the loop to stop?"
```

---

# 24. Explanation Intervention

Use when:

```text
Student lacks prerequisite knowledge
OR
multiple failed attempts indicate conceptual confusion.
```

Explanation should be:

```text
targeted
short
contextual
actionable
```

rather than a generic lecture.

---

# 25. Counterexample Intervention

Counterexamples are powerful for misconceptions.

Example:

Student believes:

```text
"Sorting always makes an algorithm faster."
```

Tutor provides:

```text
A problem where sorting adds O(n log n)
while a hash-based O(n) approach exists.
```

Then asks:

```text
"What changed?"
```

---

# 26. Analogy Intervention

Use when a concept is difficult to visualize.

Example:

```text
Stack:
Like a pile of plates.

Queue:
Like people standing in a line.
```

But analogies should not replace precise technical definitions.

---

# 27. Trace Intervention

For algorithmic reasoning:

```text
Input:
[2, 7, 11, 15]

target:
9
```

Tutor may ask:

```text
Step 1:
What is the current pointer?

Step 2:
What value is being examined?

Step 3:
What information do we learn?
```

This helps expose reasoning errors.

---

# 28. Test-Driven Intervention

When debugging:

```text
Tutor:
"Before changing the implementation,
give me one input that should fail if your hypothesis is correct."
```

This directly develops hypothesis-driven debugging.

---

# 29. Pseudocode Intervention

If implementation is the barrier:

```text
Tutor:
"Don't write Python yet.

Describe the algorithm in 4 steps."
```

The student separates:

```text
Algorithm
```

from:

```text
Syntax.
```

---

# 30. Partial Code Intervention

Used when:

```text
Concept understood
+
Implementation blocked
```

Example:

```python
left = 0
right = ______

while ______:
    mid = ______
```

The student fills the missing reasoning.

---

# 31. Full Solution Intervention

Full solutions should be the highest level of assistance.

Use when:

```text
Student explicitly requests solution
+
learning value of continued struggle is low
```

or:

```text
Student has exceeded the allowed productive-struggle threshold.
```

Even then, CodeAtlas should ideally follow with:

```text
Explain
Reconstruct
Retrieve
Transfer
```

---

# 32. Solution Exposure Protocol

If a full solution is revealed:

```text
Solution
↓
Student explains solution
↓
Student modifies / reconstructs solution
↓
Delayed retrieval
↓
New analogous problem
```

This prevents:

```text
Copy
↓
Pass
↓
Forget
```

---

# 33. AI Usage Principle

CodeAtlas may use external AI models such as:

```text
Gemini
Groq-hosted models
Other LLM providers
Local models
```

But:

> **The external LLM should generate language; CodeAtlas should control pedagogy.**

The LLM should not decide the entire learning strategy independently.

---

# 34. LLM vs CodeAtlas Responsibilities

### CodeAtlas

```text
Student state
Mistake classification
Behavior analysis
Intervention selection
Difficulty
Curriculum
Retention
Safety
```

### LLM

```text
Natural-language explanation
Question generation
Hint wording
Examples
Analogies
Feedback phrasing
Problem explanations
```

This separation is essential.

---

# 35. AI Model Router

The system should eventually support:

```text
Fast Model
↓
Simple hint / syntax / formatting

Reasoning Model
↓
Complex debugging / conceptual reasoning

Code Model
↓
Code analysis / generation

Local Model
↓
Privacy-sensitive tasks
```

The router chooses the cheapest adequate model.

---

# 36. Model Independence

CodeAtlas should not be architecturally tied to one provider.

Use an abstraction:

```text
LLMProvider
├── GeminiProvider
├── GroqProvider
├── LocalProvider
└── FutureProvider
```

The tutoring engine should communicate with:

```text
TutorModelInterface
```

rather than directly with Gemini/Groq APIs.

---

# 37. Prompt Architecture

The LLM prompt should be assembled from structured context.

Conceptually:

```text
SYSTEM
+
TUTOR POLICY
+
STUDENT STATE
+
CURRENT PROBLEM
+
CURRENT CODE
+
CURRENT ERROR
+
BEHAVIORAL SIGNALS
+
INTERVENTION TYPE
+
OUTPUT CONSTRAINTS
```

---

# 38. Prompt Rule

The prompt should explicitly prevent unnecessary solution disclosure.

Example:

```text
You are acting as a coding tutor.

The student's current objective is:
[objective]

Detected issue:
[issue]

Preferred intervention:
[intervention]

Do not provide the complete solution unless:
[conditions]

Ask one focused question at a time when using
Socratic tutoring.
```

---

# 39. One Question at a Time

Socratic tutoring should avoid:

```text
"What is the complexity?
Why does this work?
What happens here?
What should the pointer do?
Can you optimize it?"
```

Instead:

```text
"What does `right` represent in your current algorithm?"
```

Then adapt based on the answer.

---

# 40. Conversational State

The tutor must remember the current reasoning thread.

Example:

```text
Tutor:
"What does `left` represent?"

Student:
"The first possible index."

Tutor:
"Good. After `nums[mid] < target`,
which indices can no longer contain the answer?"
```

The second question depends on the student's previous answer.

---

# 41. Misconception Detection

The tutor should identify conceptual contradictions.

Example:

```text
Student:
"Binary search works because the array is sorted."

Tutor:
"Sorting helps, but is sorting alone enough?
What additional property does binary search exploit?"
```

This probes understanding.

---

# 42. Misconception Correction

Do not simply say:

```text
"That's wrong."
```

Instead:

```text
"That explanation is incomplete.

Sorting allows us to determine which portion of the
search space can be eliminated.

Why does the eliminated portion remain impossible?"
```

---

# 43. Socratic Failure Handling

If the student cannot answer:

```text
Question
↓
Clarification
↓
Smaller question
↓
Conceptual hint
↓
Explanation
```

The tutor should adapt downward.

---

# 44. Student Frustration

CodeAtlas should estimate frustration only from observable interaction signals.

Possible signals:

```text
repeated failures
rapid random edits
rapid solution requests
long inactivity
negative language in messages
repeated abandonment
```

This is not a psychological diagnosis.

It is an interaction-state estimate.

---

# 45. Frustration-Aware Tutoring

If frustration appears high:

```text
Reduce unnecessary difficulty
Increase scaffolding
Break task into smaller pieces
Offer explanation
Avoid repetitive questioning
```

But do not immediately solve everything.

---

# 46. Confidence-Aware Tutoring

If the student's understanding is uncertain:

```text
Ask diagnostic question
```

rather than:

```text
Assume they don't know
```

This avoids unnecessary teaching.

---

# 47. Tutor Calibration

CodeAtlas should learn:

```text
How much help does this student need?
```

Example:

```text
Student usually solves after H1.

Therefore:
Prefer H1 before H3.
```

Another:

```text
Student often misinterprets conceptual explanations.

Therefore:
Use examples and traces first.
```

---

# 48. Intervention Effectiveness

After an intervention, measure:

```text
Did the student progress?
Did the student understand?
Did dependency increase?
Did the same mistake recur?
Did transfer improve?
```

This allows CodeAtlas to learn which tutoring methods work for the student.

---

# 49. Intervention Memory

Example:

```text
Intervention:
Boundary diagram

Result:
Student understood immediately.

Future:
Prefer visual boundary explanations.
```

Another:

```text
Intervention:
Long textual explanation

Result:
Student remained confused.

Future:
Try trace-based explanation.
```

---

# 50. Tutor Adaptation Loop

```text
Intervention
↓
Student Response
↓
Outcome
↓
Effectiveness Estimate
↓
Update Tutor Policy
```

This creates personalized tutoring.

---

# 51. Behavioral Coaching

When a behavioral weakness is detected, the tutor should coach the behavior directly.

Example:

```text
Detected:
Random debugging.

Tutor:
"Pause for a moment.

Before changing the code, write:
1. What you believe is wrong.
2. Which test would prove it."
```

The intervention teaches a debugging habit.

---

# 52. Mistake Coaching

Suppose:

```text
Mistake:
Off-by-one
```

Do not always say:

```text
"Change `<` to `<=`."
```

Instead:

```text
"What values should this loop visit?"

"Does your current condition include the final valid index?"
```

This develops boundary reasoning.

---

# 53. Repeated Mistake Protocol

If the same mistake occurs repeatedly:

```text
Occurrence 1:
Normal correction

Occurrence 2:
Targeted explanation

Occurrence 3:
Metacognitive intervention

Occurrence 4:
Dedicated practice

Occurrence 5+:
Prerequisite investigation
```

Exact thresholds should be configurable.

---

# 54. Copying Detection

CodeAtlas should detect possible solution copying through:

```text
Large code insertion
AI-generated code acceptance
Similarity to revealed solution
Sudden complexity jump
No intermediate reasoning
```

This should be treated as:

```text
Evidence of solution dependency
```

rather than a moral judgment.

---

# 55. Copying Intervention

Example:

```text
"It looks like most of this implementation was introduced
without the intermediate reasoning.

Let's pause.

Can you explain why this loop maintains the invariant
we need?"
```

The system tests understanding.

---

# 56. Code Review Mode

CodeAtlas may review:

```text
Correctness
Readability
Complexity
Testing
Architecture
Naming
Abstraction
Maintainability
```

But feedback should be prioritized.

Do not overwhelm the student with 25 comments.

---

# 57. Feedback Prioritization

Feedback priority:

```text
1. Correctness
2. Fundamental misconception
3. Complexity
4. Testing
5. Design
6. Style
```

Style should not dominate when the algorithm is incorrect.

---

# 58. Code Review Example

Instead of:

```text
10 style comments
```

CodeAtlas might say:

```text
"Your implementation is correct.

The most important improvement is complexity:
the nested loop makes this O(n²).

Before I explain how to optimize it,
what information are you recomputing?"
```

---

# 59. Test Generation

The tutor can help generate tests, but should sometimes ask the student to generate them first.

Example:

```text
"Give me three cases that could break this implementation."
```

Then CodeAtlas evaluates the tests.

---

# 60. Test Quality Feedback

Instead of:

```text
"You need more tests."
```

say:

```text
"Your tests cover normal inputs,
but none tests the smallest valid input.

What happens when the array has one element?"
```

---

# 61. Complexity Coaching

The tutor should ask:

```text
"What is the dominant operation?"

"How many times can this loop execute?"

"Can this nested loop be bounded differently?"
```

This trains complexity reasoning.

---

# 62. Requirement Coaching

Before coding:

```text
"What constraints matter most here?"

"What should happen for an empty input?"

"Are duplicates allowed?"
```

This reduces misunderstood requirements.

---

# 63. Reflection After Problem

After significant problems, CodeAtlas may ask:

```text
What was the hardest part?

What mistake did you make?

What signal could have helped you catch it earlier?

Would you approach a similar problem differently?
```

Reflection should be short and purposeful.

---

# 64. Post-Solution Learning

Solving a problem is not necessarily the end.

CodeAtlas may trigger:

```text
Solution
↓
Explain
↓
Reflect
↓
Generalize
↓
Transfer
↓
Delayed Retrieval
```

---

# 65. Delayed Follow-Up

Example:

```text
Today:
Sliding Window

Three days later:
"Without looking at your previous solution,
what condition tells you to move the left pointer?"
```

This tests retention.

---

# 66. Tutor Session State

A session should maintain:

```text
SessionState
{
    active_problem,
    current_goal,
    current_intervention,
    hint_level,
    attempts,
    mistakes,
    hypotheses,
    tests,
    questions,
    code_revisions,
    frustration_estimate,
    progress_estimate
}
```

---

# 67. Tutor State Machine

The tutoring engine can be modeled as:

```text
OBSERVE
   ↓
DIAGNOSE
   ↓
WAIT / INTERVENE
   ↓
OBSERVE RESPONSE
   ↓
EVALUATE
   ↓
ADAPT
```

More detailed:

```text
                 ┌───────────┐
                 │  OBSERVE  │
                 └─────┬─────┘
                       ▼
                 ┌───────────┐
                 │ DIAGNOSE  │
                 └─────┬─────┘
                       ▼
              ┌─────────────────┐
              │ Need Intervention?│
              └───────┬─────────┘
                  No  │  Yes
                      │
          ┌───────────┘
          ▼
       WAIT          INTERVENE
          │              │
          └──────┬───────┘
                 ▼
              OBSERVE
                 │
                 ▼
              EVALUATE
                 │
                 ▼
               ADAPT
```

---

# 68. Tutor Decision Matrix

| Situation                               | Preferred Action             |
| --------------------------------------- | ---------------------------- |
| Minor syntax error                      | Minimal hint                 |
| Known concept, small bug                | Socratic question            |
| Repeated bug                            | Targeted coaching            |
| Conceptual misconception                | Explanation + example        |
| Strategy fixation                       | Alternative perspective      |
| Weak testing                            | Test-design prompt           |
| Weak complexity reasoning               | Complexity questions         |
| Early hint request                      | Ask for current hypothesis   |
| High frustration                        | Reduce task complexity       |
| Solution explicitly requested           | Controlled solution exposure |
| Strong performance                      | Increase challenge           |
| Strong implementation, weak recognition | Recognition exercise         |

---

# 69. Tutor Guardrails

The tutor must avoid:

```text
❌ Solving every problem immediately
❌ Giving unnecessary hints
❌ Repeating the same explanation
❌ Asking endless Socratic questions
❌ Punishing mistakes
❌ Hiding useful information indefinitely
❌ Optimizing for engagement instead of learning
❌ Creating dependency
❌ Pretending certainty when uncertain
```

---

# 70. Anti-Dependency Rule

A successful tutor should eventually become:

```text
less necessary
```

not:

```text
more necessary.
```

Therefore CodeAtlas should periodically measure:

```text
Independent Success
Hint Dependency
Solution Dependency
Transfer
Delayed Retrieval
```

---

# 71. Tutor Success Metric

A naive metric:

```text
Problems solved after tutor help.
```

Better:

```text
Problems solved independently
after previous tutoring.
```

Best:

```text
Unfamiliar problems solved independently
after a delay.
```

---

# 72. Tutoring Evaluation

Each intervention can have an outcome:

```text
INTERVENTION_SUCCESS
PARTIAL_SUCCESS
NO_PROGRESS
MISUNDERSTOOD
OVER_ASSISTED
```

These outcomes should feed the tutor model.

---

# 73. Tutor Quality Metrics

Potential metrics:

```text
Learning Gain
Independent Recovery Rate
Hint Reduction
Repeated Mistake Reduction
Transfer Success
Delayed Retention
Intervention Efficiency
Student Reasoning Quality
```

---

# 74. Intervention Efficiency

A useful concept:

```text
Intervention Efficiency =
Learning Gain / Assistance Level
```

A student who learns after one small hint is demonstrating better tutoring efficiency than one who needs a complete solution.

---

# 75. Tutor Personalization

Over time, CodeAtlas should learn:

```text
Student prefers examples vs abstractions
Student benefits from traces
Student responds well to questions
Student needs visual explanations
Student tends to overthink
Student tends to code too quickly
Student requests hints too early
```

But these should remain:

```text
learning preferences / interaction patterns
```

not personality labels.

---

# 76. Example Personalized Tutor

Student profile:

```text
Strong:
Implementation
Algorithms

Weak:
Debugging
Edge Cases

Behavior:
Codes quickly
Tests late
```

Tutor behavior:

```text
Before implementation:
Ask for one edge case.

After failure:
Ask for hypothesis.

Before giving hint:
Ask what has been tested.

After solution:
Require explanation of bug.
```

The tutor is now adapting to the student.

---

# 77. Full Example

Problem:

```text
Find the first occurrence of target in a sorted array.
```

Student submits:

```python
while left < right:
    mid = (left + right) // 2

    if arr[mid] == target:
        return mid
```

Tests fail.

---

### Stage 1 — Observe

CodeAtlas detects:

```text
Binary Search
+
Possible boundary issue
```

No intervention yet.

---

### Stage 2 — Student asks

```text
"Why is this failing?"
```

Tutor:

```text
"What should happen if `arr[mid] == target`
but there may still be another occurrence earlier?"
```

---

### Stage 3 — Student responds

```text
"I need to keep searching left."
```

Tutor:

```text
"Exactly. What should happen to `right` in that case?"
```

---

### Stage 4 — Student fixes

Student changes:

```python
right = mid - 1
```

Tutor observes.

---

### Stage 5 — New failure

Student's loop now misses the answer.

CodeAtlas detects:

```text
Boundary semantics inconsistent.
```

Tutor:

```text
"Let's stop changing the code for a moment.

What does `right` represent in your current implementation?"
```

---

### Stage 6 — Student discovers

```text
"Maybe it represents the last possible index."
```

Tutor:

```text
"Good.

If `mid` is a valid candidate but you're still looking
for an earlier occurrence, should `mid` remain a candidate?"
```

Student:

```text
"Yes."
```

Now the student can derive the correct boundary update.

---

# 78. Why This Matters

The tutor did not merely fix:

```text
right = mid - 1
```

It taught:

```text
Boundary semantics
+
Invariant reasoning
```

That knowledge can transfer to future binary-search problems.

---

# 79. Full Tutoring Loop

```text
Student writes code
        ↓
CodeAtlas observes
        ↓
Detects event
        ↓
Updates learner state
        ↓
Diagnoses problem
        ↓
Determines learning objective
        ↓
Chooses intervention
        ↓
Generates response
        ↓
Student responds
        ↓
Evaluates understanding
        ↓
Updates learner model
        ↓
Continues / escalates / stops
```

---

# 80. Long-Term Objective

The Tutoring Engine should gradually transform the student's behavior from:

```text
"I don't know.
Tell me."
```

to:

```text
"I don't know.
Let me investigate."
```

and eventually:

```text
"I don't know.
Here is my hypothesis, evidence,
and next experiment."
```

That behavioral transformation is one of the strongest indicators that CodeAtlas is actually teaching programming.

---

# 81. Final Principle

> **CodeAtlas should not be the student's coding replacement. It should be the system that makes the student increasingly capable of replacing CodeAtlas.**

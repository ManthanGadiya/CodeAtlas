# CodeAtlas — Evaluation Framework

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define how CodeAtlas measures learning, tutoring quality, personalization, adaptation, model accuracy, and long-term student improvement.

---

# 1. Purpose

CodeAtlas is not successful merely because:

- code executes,
- the AI gives correct answers,
- problems are generated,
- the student completes tasks,
- or the UI feels intelligent.

The actual objective is:

> **Determine whether CodeAtlas measurably improves the student's programming ability over time.**

Therefore evaluation must operate at multiple levels:

```text
System
   ↓
AI Components
   ↓
Student Interaction
   ↓
Learning
   ↓
Long-Term Transfer
````

---

# 2. Core Evaluation Principle

The primary metric should NOT be:

```text
Problems Solved
```

Instead:

```text
Learning Gain
+
Retention
+
Transfer
+
Independence
```

A student who solves fewer problems but becomes substantially more capable may be progressing better than a student who solves hundreds of easy problems.

---

# 3. Evaluation Layers

CodeAtlas should evaluate five major layers.

```text
Layer 1 — Software Correctness
Layer 2 — AI Correctness
Layer 3 — Personalization Quality
Layer 4 — Learning Effectiveness
Layer 5 — Long-Term Student Growth
```

---

# 4. Layer 1 — Software Correctness

This evaluates whether CodeAtlas itself works correctly.

Metrics include:

```text
API reliability
Database correctness
Code execution correctness
Sandbox isolation
Event recording accuracy
Authentication correctness
Latency
Availability
Data consistency
```

---

# 5. Layer 2 — AI Correctness

Each AI component requires separate evaluation.

```text
Mistake Classifier
Mastery Estimator
Difficulty Estimator
Problem Generator
Hint Generator
Explanation Generator
Recommendation Engine
```

A single "AI accuracy" number is insufficient.

---

# 6. Layer 3 — Personalization Quality

The system should be evaluated on whether its decisions actually reflect the student.

Example:

If a student repeatedly struggles with:

```text
Binary Search Boundaries
```

CodeAtlas should eventually detect this.

The evaluation question becomes:

> Did the system identify the weakness accurately and respond appropriately?

---

# 7. Layer 4 — Learning Effectiveness

This is the most important layer.

Measure:

```text
Pre-intervention ability
        ↓
CodeAtlas intervention
        ↓
Post-intervention ability
```

The difference represents learning gain.

---

# 8. Layer 5 — Long-Term Growth

A good tutoring system should produce durable improvement.

Therefore CodeAtlas should measure:

```text
1 day later
7 days later
30 days later
```

and eventually longer periods.

---

# 9. Evaluation Philosophy

CodeAtlas should follow:

> **Evidence over intuition.**

Do not claim:

```text
"The student learned."
```

simply because:

```text
"The student answered correctly."
```

Instead ask:

```text
Can they reproduce it later?
Can they solve a variation?
Can they explain it?
Can they recognize when to use it?
Can they solve it independently?
```

---

# 10. Student Performance Metrics

Core metrics:

```text
Accuracy
Success Rate
Attempts
Time to Solution
Hint Usage
Test Quality
Revision Count
Debugging Efficiency
Complexity Awareness
Transfer Success
Retention Success
```

---

# 11. Problem Success Rate

Basic metric:

```text
Success Rate =
Successful Problems / Attempted Problems
```

However, this metric should be segmented by:

```text
skill
difficulty
problem type
hint usage
attempt number
```

---

# 12. Independent Success Rate

A more useful metric:

```text
Independent Success Rate =
Problems solved without solution reveal
and without excessive hints
```

This should receive more importance than raw success rate.

---

# 13. Hint Dependency

Track:

```text
Hints requested
Hints available
Hint level
Time before hint
Result after hint
```

Example:

```text
Student A:
10 problems
8 hints
```

versus:

```text
Student B:
10 problems
2 hints
```

Both may have:

```text
8/10 correct
```

but demonstrate different levels of independence.

---

# 14. Hint Efficiency

Measure:

```text
Hint Efficiency =
Successful Progress After Hint
/
Hints Requested
```

A good hint should move the student forward without solving the problem for them.

---

# 15. Hint Escalation

CodeAtlas should track:

```text
Hint 1
→ conceptual direction

Hint 2
→ strategy

Hint 3
→ more specific clue

Hint 4
→ near-solution guidance
```

The evaluation should determine whether escalation occurs appropriately.

---

# 16. Time-to-Solution

Measure:

```text
T_initial
T_final
```

But raw time is insufficient.

A student becoming faster while losing correctness is not necessarily improving.

Therefore analyze:

```text
Time
+
Correctness
+
Difficulty
+
Independence
```

together.

---

# 17. Debugging Efficiency

CodeAtlas should evaluate:

```text
Time to identify bug
Number of revisions
Number of failed tests
Number of random edits
Correct diagnosis
Final correction
```

Possible metric:

```text
Debugging Efficiency =
Correct Diagnosis / Debugging Effort
```

---

# 18. Testing Behavior

A strong programmer does not simply write code.

They validate it.

Track:

```text
Number of tests
Test diversity
Boundary tests
Edge cases
Negative cases
Random cases
```

---

# 19. Test Quality

A student writing:

```python
assert solve(5) == 10
```

is not necessarily demonstrating strong testing.

A stronger evaluation considers:

```text
normal case
boundary case
empty input
minimum input
maximum input
invalid input
```

---

# 20. Test Coverage

Where technically feasible, CodeAtlas may measure:

```text
line coverage
branch coverage
condition coverage
```

However:

> High test coverage does not automatically mean high test quality.

---

# 21. Code Revision Analysis

Track the evolution:

```text
Version 1
    ↓
Version 2
    ↓
Version 3
    ↓
Final
```

Analyze:

```text
what changed
why it changed
whether the change fixed the issue
whether new bugs were introduced
```

---

# 22. Mistake Metrics

For every mistake:

```text
category
severity
frequency
skill
context
time
resolution
recurrence
```

Example:

```text
Off-by-one
Occurrences: 8
Resolved: 6
Recurrence: 3
```

---

# 23. Mistake Recurrence Rate

Important metric:

```text
Mistake Recurrence Rate =
Repeated Mistakes / Total Mistakes
```

A decreasing recurrence rate indicates learning.

---

# 24. Mistake Resolution Rate

Measure:

```text
Mistakes successfully corrected
/
Mistakes encountered
```

But this should not be interpreted alone.

A student might repeatedly fix mistakes using AI without understanding them.

Therefore combine it with:

```text
Delayed independent performance
```

---

# 25. Mistake-to-Mastery Transition

CodeAtlas should track:

```text
Mistake
   ↓
Explanation
   ↓
Guided Practice
   ↓
Independent Practice
   ↓
Delayed Retrieval
   ↓
Mastery
```

This entire transition should be measurable.

---

# 26. Skill Mastery Metrics

Each skill should maintain:

```text
Mastery
Confidence
Evidence Count
Last Practiced
Retention
Transfer
```

Example:

```text
Skill:
Binary Search

Mastery:
0.74

Confidence:
0.88

Evidence:
31 interactions

Retention:
0.61

Transfer:
0.72
```

---

# 27. Mastery Prediction Accuracy

The system predicts:

```text
P(Student succeeds)
```

Then compare against actual outcomes.

Use:

```text
Log Loss
Brier Score
Calibration
AUC
Accuracy
```

where appropriate.

---

# 28. Calibration

Suppose CodeAtlas predicts:

```text
80% success probability
```

for 100 comparable attempts.

Approximately:

```text
80
```

should succeed.

If only:

```text
55
```

succeed, the model is poorly calibrated.

---

# 29. Brier Score

For binary outcomes:

```text
Brier Score =
1/N Σ(prediction - outcome)²
```

Lower is better.

This is useful for evaluating mastery and success predictions.

---

# 30. Difficulty Prediction

Every generated or curated problem should have an estimated difficulty.

CodeAtlas can compare:

```text
Predicted Difficulty
vs
Observed Student Performance
```

Possible dimensions:

```text
Conceptual Difficulty
Implementation Difficulty
Reasoning Difficulty
Debugging Difficulty
Time Difficulty
```

---

# 31. Difficulty Calibration

Example:

```text
Predicted:
Medium

Observed:
95% of strong students solved immediately
```

Then the problem was probably too easy.

The difficulty model should update accordingly.

---

# 32. Problem Quality Metrics

Generated problems should be evaluated for:

```text
Correctness
Uniqueness
Skill Alignment
Difficulty
Clarity
Testability
Edge Cases
Solution Validity
Learning Value
```

---

# 33. Problem Diversity

Avoid generating:

```text
20 variations
```

of the same problem.

Measure semantic similarity between problems.

Possible tools:

```text
Embeddings
AST similarity
Concept overlap
Template similarity
```

---

# 34. Problem Leakage

The system must detect whether a problem is too similar to previously solved material.

Example:

```text
Previous:
"Find the longest substring without repeating characters."

New:
"Find the maximum length substring containing no duplicate characters."
```

This may test recognition rather than understanding.

---

# 35. Transfer Evaluation

Transfer problems should intentionally alter:

```text
surface form
domain
input format
story
implementation details
```

while preserving the underlying concept.

---

# 36. Transfer Score

Example:

```text
Transfer Score =
Successful Novel Applications
/
Novel Applications Attempted
```

This should be one of the major learning metrics.

---

# 37. Retention Evaluation

A skill should not be considered fully mastered immediately after learning.

CodeAtlas should schedule delayed retrieval.

Example:

```text
Day 0
Learn

Day 1
Retrieve

Day 3
Retrieve

Day 7
Retrieve

Day 14
Retrieve
```

---

# 38. Retention Score

Possible definition:

```text
Retention Score =
Successful Delayed Retrieval
/
Delayed Retrieval Attempts
```

This should be tracked separately from immediate accuracy.

---

# 39. Forgetting Curve Evaluation

For each skill, track:

```text
Time Since Practice
vs
Probability of Successful Retrieval
```

This allows CodeAtlas to estimate the student's personalized forgetting curve.

---

# 40. Learning Velocity

Measure how quickly mastery increases.

Example:

```text
Learning Velocity =
ΔMastery / Time
```

This can help determine:

```text
fast learner
slow learner
currently struggling
```

But it should not be used as a permanent label.

---

# 41. Learning Efficiency

A stronger metric:

```text
Learning Efficiency =
Learning Gain
/
Learning Effort
```

Effort can include:

```text
time
attempts
hints
```

---

# 42. AI Tutor Evaluation

Tutor responses should be evaluated on:

```text
Correctness
Relevance
Clarity
Pedagogical value
Hint quality
Non-spoilage
Personalization
Consistency
```

---

# 43. Hint Quality

A good hint should:

```text
1. Identify the relevant direction.
2. Avoid directly giving the answer.
3. Match the student's current state.
4. Address the actual misconception.
5. Enable independent progress.
```

---

# 44. Hint Spoilage

A hint becomes too strong if it essentially reveals:

```text
the algorithm
the implementation
the exact code
```

without requiring student reasoning.

Track:

```text
Hint Strength
vs
Student Independence
```

---

# 45. Explanation Quality

Explanations should be evaluated against:

```text
Correctness
Completeness
Conceptual depth
Student level
Examples
Counterexamples
Complexity
Reasoning
```

---

# 46. Personalization Score

CodeAtlas should demonstrate that recommendations actually use student information.

Compare:

```text
Personalized Recommendation
```

against:

```text
Generic Recommendation
```

and measure learning outcomes.

---

# 47. Personalization Experiment

Example:

```text
Group A:
Generic problem sequence

Group B:
Adaptive CodeAtlas sequence
```

Compare:

```text
learning gain
retention
transfer
time
engagement
```

---

# 48. Recommendation Quality

The recommendation engine should optimize for:

```text
Expected Learning Gain
```

not:

```text
Expected Probability of Solving
```

Otherwise it will continuously recommend easy problems.

---

# 49. Exploration Rate

Measure how often CodeAtlas intentionally tests uncertain skills.

Example:

```text
80% exploitation
20% exploration
```

This should be configurable and evaluated experimentally.

---

# 50. Frustration Detection

CodeAtlas should monitor signals such as:

```text
Repeated failures
Long inactivity
Rapid random edits
Repeated hint requests
Repeated solution reveals
Abandonment
```

These are signals, not proof.

---

# 51. Frustration Response Evaluation

The system should determine whether adaptation improves outcomes.

Possible responses:

```text
reduce difficulty
change explanation
switch representation
provide smaller subproblem
switch topic temporarily
```

Measure:

```text
Recovery Rate
```

---

# 52. Recovery Rate

```text
Recovery Rate =
Students returning to productive behavior
/
Students entering detected struggle state
```

---

# 53. Overhelping Detection

A major risk is:

> CodeAtlas becomes so helpful that the student stops thinking.

Track:

```text
hint frequency
solution reveal frequency
AI-generated code acceptance
independent success
```

A system that increases completion but decreases independence is failing.

---

# 54. AI Dependency Score

Potential metric:

```text
Dependency Score =
AI-assisted successful tasks
/
Total successful tasks
```

This must be interpreted carefully.

A better long-term indicator is:

```text
AI usage ↓
Independent performance ↑
```

while difficulty remains constant or increases.

---

# 55. The "Disappear" Metric

One of the most important long-term metrics:

> **How often can the student solve problems without CodeAtlas?**

The ideal trend is:

```text
CodeAtlas assistance
████████████████
        ↓
██████████
        ↓
██████
        ↓
███

Student capability
███
   ↓
██████
   ↓
██████████
   ↓
████████████████
```

---

# 56. Longitudinal Evaluation

Track progress over:

```text
Daily
Weekly
Monthly
Semester
Year
```

Metrics:

```text
Skill growth
Problem difficulty
Independence
Retention
Transfer
Debugging ability
```

---

# 57. Baseline Assessment

Before using CodeAtlas:

```text
Diagnostic Assessment
```

should establish:

```text
Initial skill state
```

Without a baseline, improvement is difficult to quantify.

---

# 58. Post-Assessment

After a defined learning period:

```text
Equivalent Assessment
```

should measure improvement.

The post-assessment should avoid simply repeating training questions.

---

# 59. Pre/Post Test Design

Bad:

```text
Pre:
Binary search problem A

Training:
Binary search problem A

Post:
Binary search problem A
```

This measures memorization.

Better:

```text
Pre:
Problem A

Training:
Problems B,C,D

Post:
Novel Problem E
```

---

# 60. Counterfactual Evaluation

A major research direction is:

> What would have happened if CodeAtlas had recommended something else?

This can eventually be studied using:

```text
A/B testing
Contextual bandits
Off-policy evaluation
```

---

# 61. A/B Testing

Potential experiments:

```text
A:
Fixed curriculum

B:
Adaptive curriculum
```

or:

```text
A:
Generic hints

B:
Personalized hints
```

---

# 62. Experiment Logging

Every experiment should record:

```text
Experiment ID
Student
Condition
Timestamp
Treatment
Outcome
Model Version
```

---

# 63. Statistical Significance

For larger-scale future studies, use appropriate statistical tests.

Potential methods:

```text
t-test
Mann–Whitney U
Chi-square
ANOVA
Regression
Mixed-effects models
```

The test should match the data.

---

# 64. Effect Size

Statistical significance alone is insufficient.

Measure:

```text
Effect Size
```

because a tiny improvement may be statistically significant but practically useless.

---

# 65. Confidence Intervals

Major metrics should ideally report:

```text
Estimate
+
Confidence Interval
```

Example:

```text
Learning Gain:
+18.4%

95% CI:
[12.1%, 24.7%]
```

---

# 66. Single-Student Evaluation

CodeAtlas initially targets one student.

Therefore traditional population-level evaluation is difficult.

The system should instead use:

```text
N-of-1 experimentation
```

---

# 67. N-of-1 Design

The same student can experience different conditions over time.

Example:

```text
Baseline
   ↓
Adaptive
   ↓
Baseline
   ↓
Adaptive
```

This allows comparison within the same individual.

---

# 68. Caution With N-of-1

Learning is cumulative.

Therefore:

```text
Week 1
```

is not perfectly comparable to:

```text
Week 4
```

because the student has changed.

Evaluation must account for this.

---

# 69. Sequential Evaluation

Better approach:

```text
Repeated measurements
+
time-series analysis
```

Track:

```text
skill
difficulty
retention
behavior
```

over time.

---

# 70. Regression Testing

Every CodeAtlas release should test:

```text
Existing functionality
```

so that improving AI does not break:

```text
IDE
execution
tracking
database
curriculum
```

---

# 71. AI Regression Testing

Maintain a fixed evaluation set containing:

```text
Known mistakes
Known problems
Known student states
Expected classifications
Expected tutoring behavior
```

Every model change should be evaluated against it.

---

# 72. Golden Dataset

Create a curated dataset:

```text
golden/
├── mistakes
├── hints
├── problems
├── explanations
├── mastery_cases
└── recommendations
```

This becomes the stable evaluation benchmark.

---

# 73. Human Annotation

Human reviewers should label:

```text
Mistake Category
Difficulty
Problem Quality
Hint Quality
Explanation Quality
```

These labels become ground truth.

---

# 74. Inter-Rater Agreement

When multiple reviewers are used, evaluate agreement.

Possible metrics:

```text
Cohen's Kappa
Fleiss' Kappa
Krippendorff's Alpha
```

This determines whether the labeling task itself is reliable.

---

# 75. Evaluation Dashboard

CodeAtlas should eventually expose an internal dashboard.

Example:

```text
┌────────────────────────────────────┐
│         CODEATLAS EVALUATION       │
├────────────────────────────────────┤
│ Mastery Gain             +17.2%    │
│ Retention                81%       │
│ Transfer                 74%       │
│ Independent Success      68%       │
│ Hint Dependency          ↓ 21%     │
│ Mistake Recurrence       ↓ 34%     │
│ Avg Difficulty           ↑         │
└────────────────────────────────────┘
```

---

# 76. Student Dashboard

The student should see meaningful metrics.

Recommended:

```text
Skills improving
Skills at risk
Recent mistakes
Retention
Problem difficulty
Independence
Weekly learning trend
```

Avoid overwhelming the student with model internals.

---

# 77. AI Transparency

For major decisions, the student should be able to ask:

```text
"Why did CodeAtlas give me this?"
```

The system should answer using evidence.

Example:

```text
You are practicing recursion because:

• You made 4 recursion-state mistakes recently.
• Your estimated mastery is 0.48.
• You haven't practiced recursion in 9 days.
• You succeeded when guided but struggled independently.
```

---

# 78. Evaluation of Explanations

The explanation itself should not expose sensitive internal information unnecessarily.

Use:

```text
student-readable evidence
```

rather than:

```text
raw model weights
```

---

# 79. Privacy Evaluation

Measure:

```text
Data minimization
API exposure
Retention policy compliance
Access control
Deletion correctness
Audit logging
```

---

# 80. Security Evaluation

Test:

```text
Sandbox escape
Prompt injection
Malicious code
Data exfiltration
Credential leakage
Cross-session leakage
Unauthorized access
```

---

# 81. Fairness

Even though CodeAtlas initially targets one student, future versions may support many users.

Evaluate whether recommendations systematically differ because of:

```text
language preference
device
hardware
usage pattern
```

when they should not.

---

# 82. Robustness

CodeAtlas should remain useful when:

```text
LLM unavailable
Internet unavailable
model response malformed
execution fails
database temporarily unavailable
student provides unusual input
```

---

# 83. Graceful Degradation

Example:

```text
LLM unavailable
      ↓
Use deterministic analysis
      ↓
Use predefined hints
      ↓
Continue tracking
```

The entire platform should not collapse because one AI provider fails.

---

# 84. Evaluation Priority

Metrics should be prioritized:

```text
Tier 1
Learning Gain
Retention
Transfer
Independence

Tier 2
Mastery Accuracy
Mistake Classification
Recommendation Quality

Tier 3
Hint Quality
Problem Quality
Explanation Quality

Tier 4
Latency
Cost
Engagement
```

---

# 85. Metrics That Must Not Become Optimization Targets

Be careful with:

```text
Daily Active Users
Session Duration
Problems Completed
Hints Used
AI Messages
```

Optimizing these directly can produce harmful behavior.

For example:

```text
More session time
≠
More learning
```

---

# 86. Anti-Gaming Mechanisms

The student should not be able to artificially inflate mastery by:

```text
repeating easy problems
guessing
copying solutions
using hints excessively
```

Therefore mastery evidence must account for:

```text
difficulty
novelty
independence
transfer
retention
```

---

# 87. Learning Score

A possible composite score:

```text
LearningScore =
0.30 × MasteryGain
+ 0.25 × Transfer
+ 0.20 × Retention
+ 0.15 × Independence
+ 0.10 × DebuggingImprovement
```

These weights are initial hypotheses, not permanent truths.

They must be validated experimentally.

---

# 88. Why Composite Scores Are Dangerous

A single score can hide important failures.

Example:

```text
LearningScore = 82
```

could hide:

```text
Retention = 35%
```

Therefore always expose the underlying dimensions.

---

# 89. Recommended Core Evaluation Vector

Instead of relying on one score:

```text
StudentProgress =
{
    mastery_gain,
    retention,
    transfer,
    independence,
    debugging,
    reasoning,
    problem_difficulty,
    hint_dependency
}
```

---

# 90. Minimum Viable Evaluation

Version 1 should measure at least:

```text
1. Problem success
2. Time to solution
3. Attempts
4. Hint usage
5. Mistake categories
6. Mistake recurrence
7. Skill mastery
8. Retention
9. Transfer
10. Independent success
```

---

# 91. Version 2 Evaluation

Add:

```text
BKT evaluation
IRT evaluation
Difficulty calibration
Problem diversity
Hint quality
Recommendation quality
Behavior prediction
```

---

# 92. Version 3 Evaluation

Add:

```text
Contextual bandit evaluation
Deep knowledge tracing
Personalized forgetting
Learning-gain prediction
Counterfactual evaluation
```

---

# 93. Version 4 Research Evaluation

Evaluate:

```text
Personalized learning policies
Long-term independence
Generalization across domains
Self-improving curriculum
Human-AI learning interaction
```

---

# 94. Success Criteria

CodeAtlas should eventually demonstrate:

```text
↑ Mastery
↑ Retention
↑ Transfer
↑ Problem Difficulty
↑ Independence

↓

Hint Dependency
Mistake Recurrence
Random Debugging
AI Dependency
```

---

# 95. Ultimate Success Criterion

The strongest evidence that CodeAtlas works is:

```text
The student becomes better at solving unfamiliar programming
problems independently.
```

Not:

```text
The student becomes better at using CodeAtlas.
```

---

# 96. Final Evaluation Loop

```text
                 ┌──────────────┐
                 │    Student   │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Interaction  │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Evidence   │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Student Model│
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Adaptation   │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Intervention │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ New Evidence │
                 └──────┬───────┘
                        │
                        └──────────────► Evaluation
```

---

# 97. Final Principle

> **CodeAtlas should measure whether it is changing the student's capabilities, not merely changing the student's behavior inside the application.**

The final benchmark is therefore:

```text
Can the student solve harder,
more unfamiliar problems,
with less assistance,
after more time has passed?
```

If the answer is consistently **yes**, CodeAtlas is doing what it was built to do.


# CodeAtlas — Problem Generator

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define how CodeAtlas generates, selects, transforms, validates, and personalizes coding problems for a single student.

---

# 1. Purpose

The Problem Generator is responsible for creating the actual coding tasks through which CodeAtlas teaches and evaluates the student.

It must not behave like a random question generator.

A traditional platform may choose:

```text
Random Topic
+
Random Difficulty
+
Random Problem
````

CodeAtlas should choose:

```text
Student State
+
Learning Objective
+
Weak Skills
+
Mistake History
+
Retention Risk
+
Behavior
+
Current Curriculum
+
Desired Difficulty
+
Transfer Requirements
        ↓
Personalized Problem
```

The problem is therefore an **instructional instrument**, not merely an exercise.

---

# 2. Core Objective

The Problem Generator should answer:

> "What is the most useful problem this student could solve next?"

Not:

> "What problem can we generate?"

---

# 3. Generator Responsibilities

The generator is responsible for:

```text
Problem Selection
Problem Generation
Problem Mutation
Difficulty Control
Skill Targeting
Mistake Targeting
Transfer Generation
Constraint Generation
Test Generation
Solution Validation
Problem Quality
Problem Diversity
```

---

# 4. Generator Architecture

```text
                 Student State
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     Mastery       Behavior      Retention
        │             │             │
        └─────────────┼─────────────┘
                      ▼
              Learning Objective
                      │
                      ▼
              Problem Strategy
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
      Select       Generate       Mutate
        │             │             │
        └─────────────┼─────────────┘
                      ▼
                Problem Builder
                      │
                      ▼
                Validator
                      │
                 ┌────┴────┐
                 ▼         ▼
               Valid     Invalid
                 │         │
                 ▼         └── Regenerate
              Student
```

---

# 5. Problem Sources

CodeAtlas should eventually support multiple sources.

```text
P1 — Curated Problems
P2 — Generated Problems
P3 — Mutated Problems
P4 — Student-Generated Problems
P5 — Real-World Tasks
P6 — Debugging Tasks
P7 — Code Completion Tasks
P8 — Reverse Engineering Tasks
P9 — Transfer Problems
```

---

# 6. Curated Problems

Curated problems are manually designed and validated.

Advantages:

```text
High quality
Known difficulty
Known solution
Reliable test cases
Strong pedagogical value
```

These should form a strong foundation for Version 1.

---

# 7. Generated Problems

An LLM can generate:

```text
Problem statement
Constraints
Examples
Starter code
Expected behavior
Hints
Solution
Test cases
```

However:

> **Generated content must never be trusted without validation.**

---

# 8. Problem Mutation

Instead of generating every problem from scratch, CodeAtlas can transform an existing problem.

Example:

Original:

```text
Find two numbers whose sum equals target.
```

Mutations:

```text
Return indices.
Return values.
Allow duplicates.
Require sorted input.
Require streaming input.
Optimize memory.
Handle negative values.
```

This creates controlled variation.

---

# 9. Why Mutation Matters

Pure generation can create:

```text
ambiguous requirements
incorrect solutions
invalid constraints
poor difficulty calibration
```

Mutation from validated problems provides greater reliability.

Therefore:

> **Generate less. Transform more.**

At least during early versions.

---

# 10. Problem Representation

Every problem should have structured metadata.

Conceptually:

```text
Problem
{
    id,
    title,
    statement,
    domain,
    skills,
    subskills,
    difficulty,
    prerequisites,
    constraints,
    input_format,
    output_format,
    examples,
    hidden_tests,
    solution,
    hints,
    explanation,
    tags,
    estimated_time,
    target_mistakes,
    transfer_level
}
```

---

# 11. Skill Targeting

Every problem should specify:

```text
Primary Skill
Secondary Skills
Prerequisites
Targeted Weakness
```

Example:

```text
Primary:
Sliding Window

Secondary:
Arrays
Hash Maps

Target Weakness:
Forgetting when to move left pointer
```

---

# 12. Single-Objective Problems

Not every problem should test everything.

A beginner problem might target:

```text
Loops
```

while avoiding:

```text
recursion
hashing
optimization
complex parsing
```

This makes diagnosis clearer.

---

# 13. Multi-Skill Problems

Later, CodeAtlas should generate problems combining skills.

Example:

```text
Graph Traversal
+
Hash Map
+
Complexity Analysis
```

These are useful for transfer and advanced learning.

---

# 14. Problem Difficulty

Difficulty must not be represented only as:

```text
Easy
Medium
Hard
```

CodeAtlas should model multiple dimensions.

```text
Concept Difficulty
Implementation Difficulty
Reasoning Difficulty
Debugging Difficulty
Constraint Difficulty
Ambiguity
Transfer Difficulty
Time Pressure
```

---

# 15. Difficulty Vector

Conceptually:

```text
Difficulty
{
    conceptual: 0.6,
    implementation: 0.4,
    reasoning: 0.8,
    debugging: 0.7,
    constraints: 0.5,
    transfer: 0.9
}
```

This allows much finer personalization.

---

# 16. Student-Specific Difficulty

A problem is not inherently equally difficult for every student.

Example:

```text
Problem:
Hash Map frequency counting
```

For Student A:

```text
Difficulty = Easy
```

For Student B:

```text
Difficulty = Hard
```

Therefore CodeAtlas should estimate:

```text
Difficulty(problem | student)
```

rather than only:

```text
Difficulty(problem)
```

---

# 17. Zone of Productive Challenge

The ideal problem should be:

```text
not trivial
+
not impossible
```

Conceptually:

```text
Too Easy
      ↓
Comfort
      ↓
Productive Challenge
      ↓
Struggle
      ↓
Overload
```

CodeAtlas should aim around:

```text
Productive Challenge
```

---

# 18. Difficulty Adaptation

If the student performs strongly:

```text
Increase:
conceptual complexity
constraints
transfer
```

If the student struggles:

```text
Reduce:
problem scope
number of interacting concepts
```

but preserve the target skill.

---

# 19. Difficulty Example

Target:

```text
Off-by-one errors
```

Instead of increasing difficulty through unrelated complexity:

Bad:

```text
Add graphs + recursion + DP.
```

Good:

```text
Same algorithm
+
different boundary conditions
+
edge cases
+
slightly altered requirements
```

The difficulty should remain aligned with the learning objective.

---

# 20. Problem Selection vs Generation

CodeAtlas should first ask:

```text
Does a suitable existing problem already exist?
```

If yes:

```text
Select.
```

If no:

```text
Mutate.
```

If mutation cannot satisfy requirements:

```text
Generate.
```

Therefore:

```text
SELECT
  ↓
MUTATE
  ↓
GENERATE
```

is the preferred order.

---

# 21. Problem Selection Score

A candidate problem can receive:

```text
ProblemScore =
SkillRelevance
+
WeaknessRelevance
+
RetentionRelevance
+
DifficultyFit
+
TransferValue
+
Diversity
-
RepetitionPenalty
-
FrustrationRisk
```

The exact weights should be configurable.

---

# 22. Skill Relevance

A problem should strongly contribute to the current learning objective.

Example:

```text
Current objective:
Learn two-pointer reasoning.
```

A random recursion problem should have:

```text
SkillRelevance ≈ 0
```

---

# 23. Weakness Relevance

Suppose CodeAtlas detects:

```text
Repeated off-by-one mistakes.
```

The next problem may intentionally contain:

```text
inclusive boundaries
exclusive boundaries
empty input
single-element input
```

The problem becomes targeted practice.

---

# 24. Retention Relevance

If:

```text
Binary Search
```

has high forgetting risk, CodeAtlas may select a retrieval problem.

This is different from teaching binary search from scratch.

---

# 25. Diversity

The generator must avoid:

```text
Problem A:
Two Sum

Problem B:
Two Sum with different numbers

Problem C:
Two Sum with different wording
```

This creates superficial variation.

Instead:

```text
Two Sum
Frequency counting
Pair constraints
Streaming pair detection
Subarray target
```

The underlying reasoning should vary.

---

# 26. Repetition Penalty

The generator should consider recent exposure.

Example:

```text
Student solved:
3 sliding-window problems today.
```

A fourth identical problem should receive a large:

```text
RepetitionPenalty
```

unless the student specifically needs repeated practice.

---

# 27. Deliberate Repetition

Repetition is not always bad.

If the student repeatedly makes:

```text
off-by-one errors
```

CodeAtlas may intentionally generate several related problems.

But the repetition should vary:

```text
problem context
input
constraints
representation
```

while preserving the targeted skill.

---

# 28. Targeted Mistake Problems

CodeAtlas can deliberately construct problems that expose a known weakness.

Example:

```text
Weakness:
Forgets empty input handling.
```

Generate:

```text
Problem where empty input is a valid case.
```

The objective is not to trick the student.

The objective is:

> **Make the weakness visible and repairable.**

---

# 29. Mistake Exposure

The problem should naturally require the targeted reasoning.

Avoid:

```text
Artificial trick question
```

Prefer:

```text
Realistic problem where the weakness genuinely matters.
```

---

# 30. Example — Off-by-One

Known weakness:

```text
Off-by-one errors in loops.
```

Problem:

```text
Given an array, return the sum of elements
between indices L and R inclusive.
```

Why useful?

Because the student must reason about:

```text
inclusive boundaries
```

without the problem explicitly saying:

```text
"This tests off-by-one errors."
```

---

# 31. Example — Complexity Mistake

Known weakness:

```text
Student repeatedly uses O(n²) solutions.
```

Generate:

```text
Input size:
1 ≤ n ≤ 100,000
```

The constraint itself forces complexity reasoning.

The tutor can later ask:

```text
"What does this constraint tell you about the algorithm?"
```

---

# 32. Example — Wrong Algorithm

Known weakness:

```text
Student uses sorting for everything.
```

Generate a problem where:

```text
sorting works
```

but:

```text
O(n)
```

is possible.

Then evaluate whether the student recognizes the tradeoff.

---

# 33. Example — Overengineering

Known behavior:

```text
Student builds unnecessary abstractions.
```

Generate:

```text
Small problem
+
clear constraints
+
simple expected implementation
```

Then evaluate:

```text
solution complexity
implementation length
abstraction count
```

The tutor can later coach:

```text
"Which part of your design was necessary for the requirements?"
```

---

# 34. Problem Types

CodeAtlas should generate multiple kinds of activities.

```text
IMPLEMENT
DEBUG
EXPLAIN
TRACE
PREDICT
OPTIMIZE
COMPLETE
REFACTOR
DESIGN
TEST
REVERSE_ENGINEER
COMPARE
CHOOSE_ALGORITHM
```

---

# 35. Implementation Problems

Traditional coding tasks.

Example:

```text
Implement an LRU Cache.
```

Useful for:

```text
implementation
algorithm
data structures
```

---

# 36. Debugging Problems

Provide intentionally broken code.

Example:

```text
Given a binary search implementation,
find and fix the bug.
```

Useful for:

```text
debugging
error localization
reasoning
```

---

# 37. Explain Problems

Example:

```text
Explain why this algorithm is O(n log n).
```

Useful for:

```text
conceptual retention
communication
metacognition
```

---

# 38. Trace Problems

Example:

```text
Given this code and input,
predict the state after iteration 4.
```

Useful for:

```text
execution reasoning
state tracking
debugging
```

---

# 39. Predict Problems

Example:

```text
What does this program output?
```

These are useful for:

```text
language semantics
control flow
memory reasoning
```

---

# 40. Optimization Problems

Start with:

```text
Correct O(n²)
```

Then ask:

```text
Can you reduce the complexity?
```

Useful for:

```text
complexity
algorithm selection
tradeoffs
```

---

# 41. Code Completion Problems

Example:

```python
def binary_search(arr, target):
    left = 0
    right = ______

    while ______:
        ...
```

Useful for:

```text
retrieval
implementation
```

---

# 42. Refactoring Problems

Example:

```text
Given working but messy code,
improve readability without changing behavior.
```

Useful for:

```text
code quality
abstraction
maintainability
```

---

# 43. Design Problems

Advanced students can receive:

```text
Design a rate limiter.
```

or:

```text
Design a URL shortener.
```

These test:

```text
systems thinking
architecture
tradeoffs
```

---

# 44. Algorithm Selection Problems

Instead of coding:

```text
Which approach would you use?

A. Sorting
B. Hash Map
C. Nested loops
D. Heap
```

Then ask:

```text
Why?
```

This tests recognition and reasoning separately from implementation.

---

# 45. Problem Sequencing

Problems should form a progression.

Example:

```text
Concept
↓
Simple implementation
↓
Guided implementation
↓
Independent implementation
↓
Variation
↓
Transfer
↓
Mixed problem
```

---

# 46. Micro → Macro Progression

A complex topic should be decomposed.

Example:

```text
Dynamic Programming

1. Recurrence recognition
2. State definition
3. Base cases
4. Memoization
5. Tabulation
6. Space optimization
7. Problem recognition
8. Transfer
```

The generator creates problems for each subskill.

---

# 47. Prerequisite Awareness

The generator must know dependencies.

Example:

```text
Binary Search
      │
      ├── Arrays
      ├── Ordering
      ├── Loop reasoning
      └── Complexity
```

If the student lacks:

```text
loop reasoning
```

CodeAtlas should not repeatedly generate harder binary-search problems.

It should repair the prerequisite.

---

# 48. Problem Dependency Graph

Conceptually:

```text
Arrays
  ↓
Loops
  ↓
Searching
  ↓
Binary Search
  ↓
Advanced Binary Search
```

The generator can use this graph to select appropriate problems.

---

# 49. Transfer Generation

Transfer problems should preserve the underlying concept while changing surface structure.

Example:

Known:

```text
Sliding window on arrays.
```

Transfer:

```text
String substring constraint.
```

The student must recognize:

```text
same underlying reasoning
```

despite a different problem appearance.

---

# 50. Transfer Difficulty

Transfer levels:

```text
T0 — Same structure
T1 — Slight variation
T2 — Different context
T3 — Different representation
T4 — Hidden technique
T5 — Multi-concept transfer
```

---

# 51. Hidden Technique Problems

At advanced levels, the problem should not tell the student:

```text
"Use Dynamic Programming."
```

Instead:

```text
Problem statement only.
```

The student must recognize the appropriate technique.

This is essential for real-world competence.

---

# 52. Real-World Problems

CodeAtlas should eventually generate tasks such as:

```text
Parse a messy CSV
Build a log analyzer
Detect duplicate events
Implement a cache
Process streaming data
Debug an API
Optimize a database query
```

These bridge:

```text
academic problem solving
```

and:

```text
real software engineering.
```

---

# 53. Constraint Generation

Constraints strongly influence difficulty.

Example:

```text
n ≤ 100
```

allows:

```text
O(n²)
```

while:

```text
n ≤ 1,000,000
```

may require:

```text
O(n log n)
```

or:

```text
O(n)
```

Therefore constraints are part of the pedagogical design.

---

# 54. Constraint Mutation

The same problem can become a new learning task by changing constraints.

Example:

```text
Version A:
n ≤ 1,000

Version B:
n ≤ 1,000,000
```

The algorithmic requirement changes.

This is an excellent way to teach complexity.

---

# 55. Edge-Case Generation

The generator should deliberately consider:

```text
empty input
single element
maximum input
minimum input
duplicates
negative values
sorted input
reverse sorted input
all identical values
already optimal input
worst-case input
```

The exact edge cases depend on the problem.

---

# 56. Adversarial Test Generation

For advanced debugging:

```text
Generate tests that expose:
boundary errors
state errors
overflow
complexity problems
incorrect assumptions
```

The goal is to test robustness.

---

# 57. Hidden Tests

Problems should contain hidden tests that the student cannot see.

They should evaluate:

```text
correctness
edge cases
constraints
performance
```

Hidden tests are particularly useful for:

```text
logic mistakes
complexity mistakes
```

---

# 58. Visible vs Hidden Tests

Visible:

```text
Teach expected behavior.
```

Hidden:

```text
Evaluate generalization.
```

The system should balance both.

---

# 59. Problem Validation

Every generated problem must pass:

```text
Syntax Validation
Solution Validation
Test Validation
Constraint Validation
Ambiguity Check
Difficulty Check
Skill Alignment Check
```

---

# 60. Reference Solution

Every problem should ideally have a validated reference solution.

This allows CodeAtlas to verify:

```text
correctness
expected complexity
edge cases
```

The reference solution should not automatically be exposed to the student.

---

# 61. Multiple Valid Solutions

The generator must recognize that:

```text
One problem
```

may have:

```text
Multiple correct solutions.
```

Evaluation should therefore focus on:

```text
behavior
correctness
constraints
complexity
```

rather than textual similarity.

---

# 62. Solution Equivalence

Two implementations may look completely different but be equivalent.

Therefore CodeAtlas should evaluate:

```text
output equivalence
```

and:

```text
complexity constraints
```

rather than:

```text
string similarity
```

alone.

---

# 63. Problem Quality Score

Conceptually:

```text
Quality =
Correctness
+
Clarity
+
Skill Alignment
+
Difficulty Calibration
+
Test Quality
+
Transfer Value
-
Ambiguity
```

Problems below a minimum threshold should not be presented.

---

# 64. LLM Validation

Generated problems should be validated by multiple stages.

Example:

```text
Generator LLM
      ↓
Static Validator
      ↓
Code Execution
      ↓
Test Validator
      ↓
Second Model Review
      ↓
Quality Score
```

LLM agreement alone is not sufficient.

---

# 65. Code Execution Validation

For coding problems:

```text
Generate solution
↓
Compile
↓
Run visible tests
↓
Run hidden tests
↓
Check expected outputs
↓
Benchmark complexity
```

This should happen before publication.

---

# 66. Hallucination Prevention

LLMs may generate:

```text
invalid constraints
incorrect examples
impossible requirements
wrong expected outputs
```

Therefore:

> **The execution environment is the source of truth for executable behavior.**

---

# 67. Problem Regeneration

If validation fails:

```text
Invalid
↓
Diagnose failure
↓
Repair
↓
Revalidate
```

If repeated failures occur:

```text
Discard problem
```

Do not repeatedly expose low-quality generated tasks.

---

# 68. Problem Versioning

Generated problems should be versioned.

```text
Problem:
binary-search-001

Version:
1.0

Mutation:
boundary-v2

Difficulty:
0.62
```

This allows CodeAtlas to know which exact problem the student solved.

---

# 69. Problem Fingerprinting

Each problem should have a fingerprint based on:

```text
concept
structure
constraints
solution strategy
```

This helps detect superficial duplicates.

---

# 70. Semantic Deduplication

Two problems with different wording may still be essentially identical.

Example:

```text
"Find two values that sum to X."

"Locate a pair whose total equals X."
```

These should be recognized as similar.

---

# 71. Problem Diversity

Diversity should exist at multiple levels:

```text
Surface Diversity
Structural Diversity
Algorithmic Diversity
Context Diversity
Representation Diversity
```

---

# 72. Student-Generated Problems

Advanced CodeAtlas should eventually ask:

> "Create a problem that would test your current weakness."

This is powerful because problem construction itself requires understanding.

The system can then evaluate the student's problem.

---

# 73. Reverse Problem Generation

Instead of:

```text
Problem → Solution
```

CodeAtlas can create:

```text
Solution → Problem
```

Example:

```text
Given this algorithm,
what problem could it solve?
```

This tests deeper understanding.

---

# 74. Bug-Driven Problem Generation

If CodeAtlas identifies:

```text
Repeated mistake:
incorrect loop termination
```

it can generate:

```text
Correct implementation
+
subtle termination bug
```

and ask:

```text
Find the bug without executing the program.
```

This trains recognition.

---

# 75. Behavioral Problem Generation

Problems can target behavior.

If the student:

```text
asks for hints too quickly
```

generate:

```text
short problem with high solvability
+
delayed hint availability
```

The goal is to encourage:

```text
first attempt
+
hypothesis
+
test
```

before requesting help.

---

# 76. Anti-Copying Problem Generation

If copying behavior is detected:

```text
Generate novel variation
```

rather than:

```text
same problem again.
```

The student must demonstrate genuine understanding.

---

# 77. Personalized Problem Narrative

The system may personalize context.

Example:

```text
Generic:
"Given an array..."

Personalized:
"You're processing daily transaction counts..."
```

However:

> Personalization should improve understanding, not become unnecessary decoration.

---

# 78. Problem Language

The problem generator should support:

```text
Python
C
C++
Java
JavaScript
```

eventually.

The underlying learning objective should remain language-independent when appropriate.

---

# 79. Language-Specific Problems

Some problems should intentionally target language semantics.

Example:

```text
Python:
mutable default arguments

C:
pointer arithmetic

C++:
object lifetime

Java:
reference semantics
```

These belong to language-specific curricula.

---

# 80. Starter Code

Starter code should be configurable:

```text
No starter code
Function signature
Partial implementation
Buggy implementation
Scaffolded implementation
```

Difficulty can be adjusted without changing the underlying problem.

---

# 81. Starter Code as Scaffolding

Example progression:

```text
Level 1:
Function signature + pseudocode

Level 2:
Function signature

Level 3:
No starter code
```

This gradually reduces support.

---

# 82. Problem Hints

Each problem should ideally have a hint ladder:

```text
H1 — Direction
H2 — Concept
H3 — Strategy
H4 — Implementation
H5 — Partial Code
H6 — Solution
```

The tutoring engine controls when each is exposed.

---

# 83. Problem Explanation

After completion, CodeAtlas should be able to explain:

```text
Why the solution works
Why the algorithm was appropriate
Complexity
Common mistakes
Alternative approaches
Transfer opportunities
```

---

# 84. Alternative Solutions

Advanced problems should include:

```text
Brute Force
Optimized
Alternative
Tradeoff
```

Example:

```text
O(n²)
vs
O(n)
```

This teaches algorithmic decision-making.

---

# 85. Tradeoff Problems

A problem may intentionally allow multiple valid solutions.

The student must explain:

```text
Why did you choose this approach?
```

This tests engineering judgment.

---

# 86. Problem Difficulty Calibration

Initially, use expert-authored difficulty estimates.

After enough student interaction:

```text
Predicted Difficulty
        ↓
Actual Student Performance
        ↓
Calibration
```

The system learns whether its difficulty estimates are accurate.

---

# 87. Difficulty Signals

Actual difficulty can be inferred from:

```text
time_to_solution
attempt_count
hint_level
mistake_count
test_failures
abandonment
independence
```

---

# 88. Student-Specific Problem Model

Eventually:

```text
P(success | student, problem)
```

should be estimated.

This allows CodeAtlas to select problems with an appropriate probability of success.

---

# 89. Ideal Challenge Probability

An eventual advanced system could target a range such as:

```text
Expected success:
60–80%
```

rather than:

```text
Always succeed.
```

The exact range should be empirically determined.

---

# 90. Problem Selection Loop

```text
Student State
      ↓
Generate Candidates
      ↓
Score Candidates
      ↓
Filter Invalid / Duplicate
      ↓
Estimate Difficulty
      ↓
Estimate Learning Value
      ↓
Select Best Problem
      ↓
Present to Student
      ↓
Observe Outcome
      ↓
Update Models
```

---

# 91. Problem Generator and Curriculum

The curriculum decides:

```text
What should be learned?
```

The problem generator decides:

```text
What exact task should teach/evaluate it?
```

Therefore:

```text
Adaptive Curriculum
        ↓
Learning Objective
        ↓
Problem Generator
        ↓
Specific Problem
```

---

# 92. Problem Generator and Tutor

The tutor decides:

```text
How should the student be helped?
```

The problem generator decides:

```text
What should the student attempt?
```

Together:

```text
Problem
  ↓
Student
  ↓
Mistake
  ↓
Tutor
  ↓
Learning Update
  ↓
Next Problem
```

---

# 93. Problem Generator and Retention

The retention system says:

```text
Binary Search is at risk.
```

The problem generator converts that into:

```text
A retrieval problem
```

rather than:

```text
A lecture about binary search.
```

---

# 94. Problem Generator and Behavior Model

Behavior model:

```text
Student rushes into coding.
```

Generator:

```text
Generate a problem requiring
algorithm selection before implementation.
```

This turns behavioral weaknesses into practice opportunities.

---

# 95. Problem Generator and Mistake Taxonomy

Mistake model:

```text
Repeated complexity mistake.
```

Generator:

```text
Generate same conceptual problem
with larger constraints.
```

The student must now reason about scalability.

---

# 96. Adaptive Problem Types

The system should choose not only:

```text
Which problem?
```

but also:

```text
Which activity format?
```

Example:

```text
Weak recognition
→ algorithm-selection task

Weak implementation
→ coding task

Weak debugging
→ broken-code task

Weak retention
→ delayed retrieval

Weak transfer
→ unfamiliar-context problem
```

---

# 97. Problem Generator as Policy

At advanced levels, the generator can be viewed as a policy:

```text
π(problem | student_state)
```

The policy chooses the problem that maximizes expected learning.

Conceptually:

```text
Expected Learning Gain
-
Time Cost
-
Frustration Risk
```

---

# 98. Future Reinforcement Learning

Eventually CodeAtlas could experiment with:

```text
State:
Student learning state

Action:
Select problem

Reward:
Learning gain
+
retention
+
transfer
+
independence
```

This creates a reinforcement-learning formulation.

However:

> This should be a later research direction, not a Version 1 dependency.

---

# 99. Generator Safety

Generated problems must not:

```text
request secrets
require unsafe commands
execute arbitrary host operations
access private files
encourage malicious behavior
```

Execution should occur inside a sandbox.

---

# 100. Execution Sandbox

For code execution:

```text
Student Code
    ↓
Sandbox
    ↓
Resource Limits
    ↓
Tests
    ↓
Result
```

Limits should include:

```text
CPU
Memory
Execution Time
Filesystem Access
Network Access
Process Creation
```

---

# 101. Resource-Aware Problems

Constraints should match execution resources.

A problem should not require:

```text
n = 10^9
```

if the reference environment cannot realistically evaluate it.

---

# 102. Generator Observability

Each generated problem should record:

```text
generation source
model used
prompt version
validator version
difficulty estimate
quality score
mutation lineage
```

This enables debugging of the generator itself.

---

# 103. Problem Lineage

Example:

```text
Base Problem
   │
   ├── Mutation A
   │     └── Boundary Variation
   │
   ├── Mutation B
   │     └── Constraint Variation
   │
   └── Mutation C
         └── Transfer Variation
```

This helps avoid repeatedly showing related problems.

---

# 104. Prompt Versioning

LLM-generated problems should store:

```text
prompt_version
model
temperature/configuration
generation_timestamp
validation_result
```

This allows reproducibility.

---

# 105. Generator Evaluation

The generator should be evaluated on:

```text
Correctness
Relevance
Difficulty Accuracy
Learning Gain
Problem Diversity
Transfer Value
Student Engagement
Retention Gain
```

---

# 106. Offline Evaluation

Before deploying a new generator version:

```text
Generate 1,000 problems
        ↓
Validate automatically
        ↓
Sample expert review
        ↓
Measure duplication
        ↓
Measure difficulty
        ↓
Compare against previous version
```

---

# 107. Online Evaluation

After deployment:

```text
Problem
↓
Student interaction
↓
Performance
↓
Learning gain
↓
Retention
```

The generator can then be evaluated using real outcomes.

---

# 108. Problem Quality Feedback Loop

```text
Generate
↓
Validate
↓
Deploy
↓
Observe
↓
Measure
↓
Identify failures
↓
Improve generator
```

---

# 109. Generator Failure Modes

Potential failures:

```text
F1 — Incorrect problem
F2 — Incorrect solution
F3 — Ambiguous statement
F4 — Wrong difficulty
F5 — Irrelevant skill
F6 — Duplicate problem
F7 — Artificial trick
F8 — Broken tests
F9 — Excessive complexity
F10 — Poor pedagogical value
```

Each should be logged separately.

---

# 110. Problem Rejection Rules

Reject a problem if:

```text
Reference solution fails
OR
tests contradict statement
OR
requirements are ambiguous
OR
target skill is unclear
OR
difficulty is outside allowed range
OR
problem is too similar to recent tasks
```

---

# 111. Example End-to-End Generation

Student state:

```text
Strong:
Arrays

Weak:
Two-pointer recognition

Behavior:
Codes immediately

Retention:
Two-pointer concept at risk

Current objective:
Recognize two-pointer opportunities
```

Generator decides:

```text
Activity:
Algorithm Selection
```

Problem:

```text
Given a sorted array, determine whether two values
sum to target.
```

But instead of saying:

```text
"Use two pointers."
```

the student must choose an approach.

Then:

```text
If successful:
Generate implementation problem.

If failed:
Generate simpler recognition problem.

If successful but forgot later:
Schedule retrieval problem.

If repeatedly failing:
Teach prerequisite reasoning.
```

---

# 112. Advanced Problem Generation

At Level 4, CodeAtlas should eventually generate:

```text
Open-ended debugging
System design
Performance optimization
Repository-level tasks
API integration
Data pipeline tasks
Concurrency problems
Architecture tradeoffs
Real-world datasets
```

The generator should evolve from:

```text
LeetCode-style problems
```

toward:

```text
real engineering problems.
```

---

# 113. Repository-Level Problems

Advanced students may receive:

```text
"You inherited this repository.

A feature is failing under concurrent requests.

Find the bug and propose a fix."
```

This tests:

```text
code navigation
debugging
systems reasoning
testing
architecture
```

---

# 114. Real Codebase Problems

Eventually CodeAtlas should be capable of generating tasks from:

```text
Student's own projects
```

For example:

```text
Student's backend
+
known weak area
```

CodeAtlas can create:

```text
debugging challenge
refactoring task
performance challenge
testing task
```

This is one of the strongest future directions.

---

# 115. Personalized Project Problems

If the student is building:

```text
AI application
```

CodeAtlas could generate:

```text
"Your API currently makes three sequential model calls.

Can you reduce unnecessary latency?"
```

This makes learning directly relevant to the student's work.

---

# 116. Final Generator Principle

The problem generator should never ask:

> "What question should I give the student?"

It should ask:

> **"What experience will most effectively move this student's learning state forward?"**

---

# 117. Final Generation Loop

```text
                 STUDENT
                    │
                    ▼
             LEARNING STATE
                    │
                    ▼
             LEARNING OBJECTIVE
                    │
                    ▼
             PROBLEM STRATEGY
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       SELECT     MUTATE    GENERATE
          │         │         │
          └─────────┼─────────┘
                    ▼
                 VALIDATE
                    │
                    ▼
                  SCORE
                    │
                    ▼
                 PRESENT
                    │
                    ▼
                OBSERVE
                    │
                    ▼
             UPDATE STUDENT
                    │
                    └──────────────► NEXT PROBLEM
```

---

# 118. Final Design Principles

1. Generate for learning, not quantity.
2. Prefer validated problems over raw LLM generation.
3. Prefer mutation over generation when possible.
4. Target specific skills and mistakes.
5. Difficulty must be multidimensional.
6. Problems must adapt to the individual student.
7. Transfer must eventually become a major objective.
8. Problem variation must go beyond changing wording.
9. Every executable problem must be validated.
10. The generator must learn from student outcomes.
11. Repeated mistakes should influence future problem design.
12. Retention risk should influence problem selection.
13. Behavioral weaknesses should become practice opportunities.
14. The system should gradually move from academic exercises toward real engineering tasks.
15. The best problem is the one that produces the most useful learning evidence for the least unnecessary effort.

---

# 119. Final Vision

A conventional coding platform asks:

```text
"What problem do you want to solve?"
```

CodeAtlas should eventually know:

```text
"You have become strong at implementation,
but your recognition of when to use this technique
is still weak.

You also haven't retrieved it for 12 days.

So I am giving you a problem that looks different
from the ones you've solved before, but requires the
same underlying reasoning.

I won't tell you the technique."
```

That is the point where CodeAtlas stops being a **problem generator** and becomes a **personalized learning environment**.

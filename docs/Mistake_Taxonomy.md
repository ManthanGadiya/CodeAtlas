# CodeAtlas — Mistake Taxonomy

> **Version:** 0.1  
> **Status:** Foundational Specification  
> **Project:** CodeAtlas  
> **Purpose:** Define how CodeAtlas identifies, classifies, relates, stores, and learns from programming mistakes.

---

# 1. Purpose

Mistakes are one of the most valuable sources of learning evidence available to CodeAtlas.

A conventional coding platform usually treats:

```text
Wrong Answer
Runtime Error
Compilation Error
````

as the final result.

CodeAtlas must go further.

It should attempt to determine:

> **What went wrong, why it went wrong, whether it has happened before, what underlying skill it may indicate, and what intervention is most appropriate.**

For example:

```text
Wrong Answer
      ↓
Boundary condition failed
      ↓
Off-by-one error
      ↓
Repeated across 3 problems
      ↓
Boundary reasoning weakness
      ↓
Targeted intervention
      ↓
New transfer problem
```

The mistake taxonomy therefore acts as a bridge between:

```text
Code execution
      ↓
Evidence
      ↓
Diagnosis
      ↓
Learner model
      ↓
Adaptive curriculum
      ↓
Tutoring
```

---

# 2. Core Principle

CodeAtlas must distinguish between:

```text
Observed Error
```

and:

```text
Inferred Cause
```

Example:

```text
Observed:
Array index goes out of bounds.

Possible causes:
- incorrect loop boundary
- wrong array length assumption
- misunderstood indexing
- invalid input assumption
- careless implementation
```

The system must not automatically conclude:

```text
Index out of bounds = Off-by-one
```

Instead:

```text
Observation
    ↓
Candidate explanations
    ↓
Additional evidence
    ↓
Most likely classification
```

---

# 3. Taxonomy Architecture

Mistakes should be organized into multiple layers.

```text
Mistake
│
├── Surface Error
│   ├── Syntax
│   ├── Runtime
│   ├── Compilation
│   └── Test Failure
│
├── Reasoning Error
│   ├── Logic
│   ├── Algorithm
│   ├── Requirement
│   └── Assumption
│
├── Implementation Error
│   ├── Off-by-One
│   ├── State Update
│   ├── Data Handling
│   └── Control Flow
│
├── Complexity Error
│   ├── Time Complexity
│   ├── Space Complexity
│   └── Scalability
│
├── Problem-Solving Behavior
│   ├── Random Debugging
│   ├── Overengineering
│   ├── Copying
│   └── Premature Optimization
│
└── Learning / Knowledge Error
    ├── Forgotten Concept
    ├── Misconception
    ├── Transfer Failure
    └── Recognition Failure
```

---

# 4. Classification Dimensions

A mistake should not be represented using only one label.

Each mistake may contain:

```text
Mistake
├── category
├── subtype
├── severity
├── confidence
├── evidence
├── affected_skill
├── suspected_root_cause
├── recurrence
├── context
├── first_seen
├── last_seen
└── resolution_status
```

Example:

```text
Mistake:
Off-by-One

Category:
Implementation

Confidence:
0.91

Severity:
Medium

Affected Skill:
Binary Search / Boundary Handling

Recurrence:
High

Evidence:
- incorrect right boundary
- failed edge case
- same pattern seen previously
```

---

# 5. Primary Mistake Categories

CodeAtlas will initially use the following primary categories:

```text
M01 — Syntax Error
M02 — Compilation / Type Error
M03 — Runtime Error
M04 — Logic Error
M05 — Off-by-One Error
M06 — Wrong Algorithm
M07 — Complexity Mistake
M08 — Requirement Misunderstanding
M09 — Incorrect Assumption
M10 — Edge Case Failure
M11 — Testing Failure
M12 — State / Invariant Error
M13 — Data Structure Misuse
M14 — Recursion Error
M15 — Concurrency / State Error
M16 — Repeated Mistake
M17 — Copying / Solution Dependency
M18 — Overengineering
M19 — Premature Optimization
M20 — Debugging Strategy Failure
M21 — Recognition Failure
M22 — Transfer Failure
M23 — Conceptual Misconception
M24 — Forgotten Knowledge
```

The taxonomy is extensible.

---

# 6. M01 — Syntax Error

## Definition

The program violates the syntax rules of the programming language.

Examples:

```text
missing bracket
missing colon
incorrect indentation
invalid token
missing semicolon
incorrect syntax
```

Example:

```python
for i in range(10)
    print(i)
```

Classification:

```text
M01 — Syntax Error
```

---

## Learning Interpretation

A single syntax error usually provides weak evidence of conceptual weakness.

Repeated syntax errors may indicate:

```text
language familiarity weakness
syntax memory weakness
```

The system should therefore distinguish:

```text
isolated syntax mistake
```

from:

```text
persistent syntax difficulty
```

---

# 7. M02 — Compilation / Type Error

Examples:

```text
type mismatch
undefined variable
invalid function call
missing import
invalid conversion
compile-time semantic error
```

Example:

```python
x = "10"
y = x + 5
```

Potential classification:

```text
M02 — Type Error
```

---

## Learning Interpretation

Repeated errors involving a specific concept may indicate:

```text
type system misunderstanding
API misunderstanding
language semantics weakness
```

---

# 8. M03 — Runtime Error

Examples:

```text
IndexError
NullPointerException
Segmentation Fault
KeyError
Stack Overflow
Division by Zero
```

Runtime errors should be classified further when possible.

For example:

```text
IndexError
      ↓
Incorrect boundary
      ↓
Possible Off-by-One
```

The runtime error is the observation.

The deeper classification is an inference.

---

# 9. M04 — Logic Error

## Definition

The program executes successfully but produces incorrect behavior because the reasoning or implementation logic is incorrect.

Example:

```python
if age > 18:
    eligible = True
```

when the requirement is:

```text
age >= 18
```

Classification:

```text
M04 — Logic Error
M05 — Off-by-One
```

Multiple labels may be appropriate.

---

# 10. M05 — Off-by-One Error

## Definition

A boundary is incorrectly handled by one or a small number of positions.

Common examples:

```text
i < n
vs
i <= n

left <= right
vs
left < right

range(n)
vs
range(1, n)
```

---

## Important Contexts

Off-by-one errors commonly occur in:

```text
Arrays
Loops
Binary Search
Sliding Window
Two Pointer
String Processing
Prefix Sums
Dynamic Programming
```

---

## Learning Interpretation

Repeated off-by-one errors across unrelated problems are stronger evidence of:

```text
boundary reasoning weakness
```

than of weakness in any single algorithm.

---

# 11. M06 — Wrong Algorithm

## Definition

The student selects an algorithm that cannot appropriately solve the problem under the given requirements.

Example:

```text
Problem:
Find shortest path in an unweighted graph.

Student:
Uses DFS and assumes first path is shortest.
```

Possible diagnosis:

```text
Algorithm selection failure
```

---

## Important Distinction

The student may know BFS perfectly but fail to recognize that BFS applies.

Therefore CodeAtlas should distinguish:

```text
Algorithm implementation failure
```

from:

```text
Algorithm recognition failure
```

---

# 12. M07 — Complexity Mistake

## Definition

The solution is functionally correct but violates expected time or space constraints.

Example:

```text
Expected:
O(n log n)

Student:
O(n²)
```

Possible subtypes:

```text
TIME_COMPLEXITY
SPACE_COMPLEXITY
SCALABILITY
UNNECESSARY_RECOMPUTATION
INEFFICIENT_DATA_STRUCTURE
```

---

## Learning Interpretation

Repeated complexity mistakes may indicate weakness in:

```text
Complexity analysis
Algorithm selection
Data structure selection
Scalability reasoning
```

---

# 13. M08 — Requirement Misunderstanding

## Definition

The student solves a different problem from the one specified.

Examples:

```text
returns index instead of value
assumes sorted input when not stated
ignores duplicate values
returns any answer when minimum is required
```

This is particularly important because the code itself may be logically correct for the student's interpretation.

---

## Detection Sources

CodeAtlas should compare:

```text
Problem Requirements
+
Student Explanation
+
Code Behavior
+
Tests
```

---

# 14. M09 — Incorrect Assumption

## Definition

The student makes an assumption that is not guaranteed by the problem.

Examples:

```text
Input will always be sorted.
There will never be duplicates.
N will always be small.
Input will never be empty.
The graph is connected.
```

Incorrect assumptions are particularly valuable because they reveal reasoning habits.

---

# 15. M10 — Edge Case Failure

Examples:

```text
empty input
single element
maximum value
minimum value
duplicate values
negative numbers
already sorted input
reverse sorted input
disconnected graph
cycle
```

The system should record the specific edge case.

Example:

```text
Edge Case:
Empty Array

Failure:
IndexError

Affected Skill:
Array Boundary Handling
```

---

# 16. M11 — Testing Failure

A student may write technically correct code but fail to test meaningful cases.

Examples:

```text
only tests happy path
does not test empty input
does not test boundary values
does not test duplicates
does not test maximum constraints
```

Testing behavior should be treated separately from correctness.

---

# 17. M12 — State / Invariant Error

This is a high-value category for advanced programming.

## Definition

The student fails to maintain an invariant or state relationship required for correctness.

Examples:

```text
Sliding Window:
window invariant violated

Binary Search:
search-space invariant violated

Heap:
heap property violated

Graph traversal:
visited-state incorrectly maintained
```

---

## Why It Matters

Many advanced algorithmic bugs are not really syntax or logic mistakes.

They are failures to reason about:

```text
State
+
Invariant
+
Transition
```

CodeAtlas should eventually become particularly strong at identifying these errors.

---

# 18. M13 — Data Structure Misuse

Examples:

```text
Using list where set is needed
Using array instead of hash map
Using stack instead of queue
Incorrect heap usage
Incorrect graph representation
```

Potential underlying weaknesses:

```text
Data structure knowledge
Trade-off reasoning
Complexity reasoning
```

---

# 19. M14 — Recursion Error

Possible subtypes:

```text
Missing Base Case
Incorrect Base Case
Incorrect Recursive Transition
Incorrect Return Propagation
State Mutation Error
Stack Overflow
Duplicate Work
```

Example:

```python
def factorial(n):
    return n * factorial(n)
```

Classification:

```text
M14 — Recursion Error
Subtype:
Missing Base Case
```

---

# 20. M15 — Concurrency / State Error

Reserved for advanced programming.

Examples:

```text
Race condition
Deadlock
Data race
Incorrect synchronization
Shared-state corruption
Atomicity violation
```

This category becomes relevant when CodeAtlas supports languages and environments where concurrency is taught.

---

# 21. M16 — Repeated Mistake

## Definition

A substantially similar mistake appears repeatedly across different attempts.

Example:

```text
Problem 1:
Binary search → right boundary error

Problem 2:
Sliding window → right boundary error

Problem 3:
Two pointer → right boundary error
```

Possible higher-level inference:

```text
Boundary reasoning weakness
```

---

## Important Rule

A repeated mistake is not merely:

```text
same error message
```

It should ideally represent:

```text
same underlying error pattern
```

This requires semantic comparison.

---

# 22. M17 — Copying / Solution Dependency

## Definition

The student relies heavily on external or generated solutions instead of independently solving the problem.

Possible signals:

```text
solution viewed
large code pasted
large code inserted after hint
minimal modification to reference solution
solution copied after failure
```

---

## Important Distinction

CodeAtlas should not automatically accuse a student of cheating.

Instead:

```text
Evidence:
High similarity to reference solution
```

may be recorded as:

```text
Potential Solution Dependency
```

with confidence.

---

# 23. M18 — Overengineering

## Definition

The student introduces unnecessary complexity for a problem.

Examples:

```text
5 classes for a simple algorithm
unnecessary abstraction layers
complex framework for trivial task
unnecessary data structures
```

Overengineering can increase:

```text
bug surface
cognitive load
development time
maintenance cost
```

---

## Learning Interpretation

Repeated overengineering may indicate:

```text
abstraction judgment weakness
problem decomposition weakness
simplicity blindness
```

However, advanced solutions should not be penalized merely because they are sophisticated.

---

# 24. M19 — Premature Optimization

## Definition

The student optimizes before establishing correctness.

Example:

```text
Student spends 20 minutes optimizing a solution
that has not passed basic tests.
```

Potential behavioral pattern:

```text
Correctness
   ↓
should come before
   ↓
optimization
```

---

# 25. M20 — Debugging Strategy Failure

This category focuses on the process of debugging rather than the final bug.

Signals may include:

```text
random code changes
repeatedly rerunning without changing hypothesis
no targeted tests
large unrelated edits
ignoring error messages
changing multiple components simultaneously
```

---

## Example

```text
Bug exists in binary search boundary.

Student:
changes loop
changes midpoint
changes array
changes return
changes input parsing
```

without testing hypotheses.

Potential diagnosis:

```text
Debugging strategy weakness
```

---

# 26. M21 — Recognition Failure

## Definition

The student knows how to use a concept when explicitly instructed but fails to recognize when it applies.

Example:

```text
Prompt:
"Use binary search."

Student:
Solves correctly.

Different prompt:
"Find the minimum feasible value."

Student:
Uses brute force.
```

Potential diagnosis:

```text
Binary Search Implementation:
Strong

Binary Search Recognition:
Weak
```

This is a critical distinction for adaptive learning.

---

# 27. M22 — Transfer Failure

## Definition

The student demonstrates a concept in familiar contexts but fails to apply it to a sufficiently novel context.

Example:

```text
Training:
Binary search on sorted array.

Transfer:
Binary search over answer space.

Student fails.
```

Transfer failure should not automatically reduce core mastery significantly.

Instead it should primarily affect:

```text
Transfer Ability
Recognition
Generalization
```

---

# 28. M23 — Conceptual Misconception

## Definition

The student holds an incorrect mental model of a concept.

Examples:

```text
"Binary search always requires an array to be sorted."

"Hash maps always have O(1) worst-case lookup."

"BFS always finds the shortest path."

"Recursion always uses less memory than iteration."
```

The important distinction is:

```text
Implementation Bug
```

versus:

```text
Incorrect Mental Model
```

A misconception may generate many downstream bugs.

---

# 29. M24 — Forgotten Knowledge

## Definition

A previously demonstrated skill appears to have degraded after a period without successful retrieval.

Example:

```text
March:
Student solves DFS independently.

April:
Student solves DFS independently.

June:
Student cannot recall traversal implementation.
```

This may indicate:

```text
Retention decline
```

rather than:

```text
Never learned DFS
```

This distinction is critical to CodeAtlas.

---

# 30. Mistake Severity

Mistake severity should not simply mean:

```text
How bad is the code?
```

Instead it should represent educational significance.

Possible levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

## LOW

Examples:

```text
Minor syntax mistake
Typo
Variable naming mistake
```

Usually weak learning evidence.

---

## MEDIUM

Examples:

```text
Off-by-one
Missing edge case
Incorrect test
```

Potentially meaningful learning evidence.

---

## HIGH

Examples:

```text
Wrong algorithm
Complexity failure
Requirement misunderstanding
Conceptual misconception
Repeated mistake
```

Strong learning implications.

---

## CRITICAL

Reserved for cases such as:

```text
Deep misconception
Persistent repeated failure
Severe security-related programming mistake
Fundamental prerequisite weakness
```

The exact use of CRITICAL should be conservative.

---

# 31. Mistake Confidence

Every mistake classification should contain:

```text
confidence ∈ [0,1]
```

Example:

```text
Off-by-One:
confidence = 0.94
```

versus:

```text
Conceptual Misconception:
confidence = 0.37
```

The latter should trigger further diagnostic evidence rather than aggressive curriculum changes.

---

# 32. Multi-Label Classification

A single event may have multiple classifications.

Example:

```text
Student uses O(n²) solution.

Category:
Complexity Mistake

Underlying:
Wrong Algorithm

Behavior:
Premature Optimization
```

Therefore CodeAtlas should support:

```text
Primary Mistake
+
Secondary Mistakes
+
Root-Cause Hypotheses
```

---

# 33. Root Cause vs Symptom

This distinction is central.

Example:

```text
Symptom:
Wrong Answer

↓
Observed Failure:
Boundary condition

↓
Mistake:
Off-by-One

↓
Potential Cause:
Incorrect interval invariant

↓
Potential Root Cause:
Weak boundary reasoning
```

The system should not stop at the symptom.

---

# 34. Mistake Causal Chain

CodeAtlas should eventually represent:

```text
Knowledge Gap
      ↓
Incorrect Mental Model
      ↓
Wrong Reasoning
      ↓
Incorrect Implementation
      ↓
Runtime / Test Failure
```

Example:

```text
Misunderstands sliding-window invariant
            ↓
Incorrect window update
            ↓
Boundary failure
            ↓
Wrong answer
```

This gives the tutor a much better intervention target.

---

# 35. Mistake Context

Every mistake should retain context.

Example:

```text
MistakeContext
├── problem_id
├── language
├── code_revision
├── execution
├── failing_test
├── problem_difficulty
├── affected_skill
├── previous_attempts
├── hints_before_failure
└── tutor_interaction
```

The same mistake can have different meanings in different contexts.

---

# 36. Mistake Lifecycle

Every mistake can move through states.

```text
DETECTED
   ↓
CLASSIFIED
   ↓
CONFIRMED
   ↓
INTERVENTION
   ↓
RETESTED
   ↓
RESOLVED
```

Or:

```text
DETECTED
   ↓
UNCERTAIN
   ↓
MORE_EVIDENCE
```

The system should support uncertainty.

---

# 37. Mistake Recurrence

Recurrence measures whether a mistake continues appearing.

Possible levels:

```text
NONE
LOW
MEDIUM
HIGH
PERSISTENT
```

Example:

```text
Off-by-One

First occurrence:
LOW

3 occurrences:
MEDIUM

7 occurrences:
HIGH

Repeated across multiple concepts:
PERSISTENT
```

---

# 38. Cross-Problem Recurrence

A powerful CodeAtlas feature should be detecting the same underlying mistake across different problem types.

Example:

```text
Binary Search
      ↓
Boundary error

Sliding Window
      ↓
Boundary error

Two Pointer
      ↓
Boundary error

Prefix Sum
      ↓
Boundary error
```

This suggests a general reasoning weakness rather than a single algorithm problem.

---

# 39. Cross-Domain Recurrence

Even more advanced:

```text
Arrays:
boundary mistakes

Graphs:
incorrect loop termination

Recursion:
incorrect base case

DP:
incorrect state boundary
```

The surface mistakes differ.

The underlying pattern may be:

```text
Weak boundary-condition reasoning
```

CodeAtlas should eventually be able to discover such latent patterns.

---

# 40. Mistake Clustering

Future versions may cluster mistakes based on:

```text
Code structure
Error behavior
Problem context
Skill relationship
Semantic similarity
Student reasoning
```

Conceptually:

```text
Raw Mistakes
     ↓
Embedding / Feature Representation
     ↓
Clustering
     ↓
Latent Error Pattern
```

Example:

```text
Cluster:
Boundary Reasoning

Members:
- loop endpoint error
- binary search interval error
- sliding window boundary error
- substring endpoint error
```

---

# 41. Mistake-to-Skill Mapping

A mistake may affect multiple skills.

Example:

```text
Off-by-One
│
├── Array Indexing
├── Binary Search
├── Sliding Window
├── Two Pointer
└── Loop Reasoning
```

The system should maintain weighted relationships.

Example:

```text
Off-by-One
→ Boundary Handling: 0.90
→ Loop Reasoning: 0.75
→ Binary Search: 0.52
```

These weights should evolve based on evidence.

---

# 42. Mistake-to-Behavior Mapping

Mistakes may also indicate behavioral patterns.

Example:

```text
Repeated Logic Error
+
No Test Creation
+
Immediate Hint Requests
```

may indicate:

```text
Weak Debugging Strategy
```

rather than merely:

```text
Weak Algorithm Knowledge
```

---

# 43. Mistake-to-Intervention Mapping

Different mistakes should trigger different interventions.

| Mistake                      | Preferred Initial Intervention |
| ---------------------------- | ------------------------------ |
| Syntax                       | Brief correction               |
| Off-by-One                   | Boundary diagnostic            |
| Wrong Algorithm              | Recognition question           |
| Complexity                   | Complexity reasoning           |
| Requirement Misunderstanding | Requirement restatement        |
| Conceptual Misconception     | Concept diagnosis              |
| Edge Case Failure            | Test-generation exercise       |
| Debugging Strategy           | Debugging methodology coaching |
| Transfer Failure             | Novel related problem          |
| Forgotten Knowledge          | Retrieval practice             |
| Overengineering              | Simplification challenge       |

The tutor may escalate if the first intervention fails.

---

# 44. Mistake Intervention Example

Suppose:

```text
Mistake:
Wrong Algorithm

Problem:
Shortest path in unweighted graph
```

Bad tutor behavior:

```text
"Use BFS."
```

Better:

```text
"What property of the graph determines whether every edge
should be considered to have the same cost?"
```

If the student still struggles:

```text
"What traversal guarantees that nodes are explored
in increasing number of edges from the source?"
```

Only later:

```text
"This is the property that makes BFS appropriate here."
```

The mistake taxonomy should inform the tutoring strategy.

---

# 45. Mistake Resolution

A mistake should not be marked resolved merely because:

```text
student eventually got the answer.
```

Better resolution evidence:

```text
Initial mistake
      ↓
Intervention
      ↓
Immediate correction
      ↓
New related problem
      ↓
Independent success
      ↓
Delayed retrieval
      ↓
Transfer success
```

The stronger the evidence, the more confidence CodeAtlas should have that the underlying issue has been addressed.

---

# 46. Mistake Resolution Levels

Possible states:

```text
UNRESOLVED
IMMEDIATELY_CORRECTED
SHORT_TERM_RESOLVED
STABLE
TRANSFER_RESOLVED
```

Example:

```text
Off-by-One

Immediate correction:
YES

Next problem:
SUCCESS

One week later:
SUCCESS

Transfer:
SUCCESS

Status:
TRANSFER_RESOLVED
```

---

# 47. False Positive Prevention

Mistake classification can itself be wrong.

Therefore CodeAtlas should track:

```text
classification confidence
evidence source
validation status
later confirmation
```

Example:

```text
Initial:
Possible misconception — confidence 0.41

Later:
Student explains concept correctly.

Update:
Misconception confidence → 0.08
```

---

# 48. False Negative Prevention

The system should also recognize that some mistakes may remain undetected.

For example:

```text
Student solves a problem correctly
```

but used an inefficient algorithm.

If constraints are small, the error may not manifest.

Therefore CodeAtlas should analyze:

```text
Correctness
+
Complexity
+
Constraints
+
Algorithm choice
```

where feasible.

---

# 49. Mistake Evidence Sources

Possible sources:

```text
Compiler
Runtime
Test Runner
Static Analyzer
AST Analyzer
Complexity Analyzer
Code Diff
Student Explanation
Tutor Conversation
Problem Metadata
Behavior Tracker
LLM Analysis
Historical Learner Model
```

The system should combine multiple evidence sources.

---

# 50. Deterministic vs AI Classification

## Deterministic

Prefer deterministic systems for:

```text
Syntax errors
Compilation errors
Runtime errors
Test failures
Execution time
Memory usage
Basic AST patterns
Basic complexity signals
```

## AI-Assisted

LLMs can help with:

```text
Requirement misunderstanding
Conceptual misconceptions
Reasoning errors
Overengineering
Root-cause hypotheses
Semantic mistake similarity
```

The LLM should provide:

```text
classification
confidence
evidence
explanation
```

rather than simply:

```text
"Mistake: Logic Error"
```

---

# 51. Example Structured Classification

```json
{
  "mistake_id": "MST-1024",
  "primary_type": "OFF_BY_ONE",
  "secondary_types": [
    "LOGIC_ERROR",
    "EDGE_CASE_FAILURE"
  ],
  "severity": "MEDIUM",
  "confidence": 0.93,
  "affected_skills": [
    {
      "skill": "binary-search-boundaries",
      "weight": 0.91
    }
  ],
  "evidence": [
    "right boundary excludes valid candidate",
    "maximum-value test failed",
    "same pattern observed previously"
  ],
  "recurrence": "HIGH",
  "suspected_root_cause": "boundary reasoning",
  "resolution_status": "UNRESOLVED"
}
```

The production representation may differ.

---

# 52. Mistake Scoring

A mistake can conceptually receive:

```text
Mistake Impact =
Severity
× Recurrence
× Confidence
× Skill Relevance
```

This should NOT initially be used as a rigid formula.

It is a conceptual framework for prioritization.

---

# 53. Priority of Mistakes

CodeAtlas should prioritize mistakes using:

```text
High recurrence
+
High educational impact
+
High confidence
+
Important prerequisite
+
Transfer relevance
```

Example:

```text
Mistake A:
One typo

Mistake B:
Repeated incorrect complexity reasoning

Priority:
Mistake B
```

---

# 54. Mistake Suppression

Not every mistake deserves an intervention.

For example:

```text
Student types:
prnit("hello")
```

and immediately fixes it.

CodeAtlas should not generate:

```text
Today's lesson:
Python spelling errors
```

The system should suppress low-value noise.

---

# 55. Learning-Significant Mistake

A mistake becomes learning-significant when it demonstrates one or more:

```text
Recurrence
Conceptual weakness
Transfer failure
Important prerequisite weakness
Behavioral pattern
Persistent misunderstanding
```

This is the level at which it should influence curriculum.

---

# 56. Mistake Taxonomy Evolution

The taxonomy itself should evolve.

Initially:

```text
Human-designed categories
```

Later:

```text
Observed mistake data
      ↓
New patterns
      ↓
Candidate categories
      ↓
Validation
      ↓
Taxonomy extension
```

CodeAtlas should never blindly create hundreds of categories.

The taxonomy must remain useful to the learning engine.

---

# 57. Taxonomy Versioning

Every classification should record the taxonomy version.

Example:

```text
taxonomy_version:
0.1.0
```

If the taxonomy changes:

```text
0.2.0
```

Historical classifications should remain interpretable.

---

# 58. Core Rules

### Rule 1

A compiler error is not necessarily a learning problem.

### Rule 2

A wrong answer is not a sufficient diagnosis.

### Rule 3

Symptoms and root causes must be separated.

### Rule 4

One mistake should rarely determine a learner-state change.

### Rule 5

Repeated patterns are stronger evidence.

### Rule 6

Cross-problem recurrence is especially valuable.

### Rule 7

Cross-domain recurrence can reveal deeper reasoning weaknesses.

### Rule 8

Mistake confidence must be explicit.

### Rule 9

The LLM must not be the sole source of truth.

### Rule 10

Mistakes should drive intervention only when educationally meaningful.

### Rule 11

A resolved mistake should be tested again.

### Rule 12

Transfer success is stronger evidence of resolution than immediate correction.

---

# 59. Long-Term Objective

A mature CodeAtlas mistake engine should eventually move from:

```text
"What error occurred?"
```

to:

```text
"What reasoning failed?"
```

and eventually:

```text
"Why does this student repeatedly make this kind of reasoning error?"
```

The ultimate goal is not perfect error labeling.

The goal is:

```text
Mistake
   ↓
Understanding
   ↓
Intervention
   ↓
Improvement
```

---

# 60. Final Principle

> **A mistake is not merely something that went wrong in the code. It is evidence about the student's current mental model, reasoning process, behavior, or knowledge state.**

CodeAtlas should therefore treat mistakes as **learning signals**, not failures to be punished.

The best mistake classifier is not the one that produces the most labels.

It is the one that helps CodeAtlas choose a better intervention and eventually helps the student stop making the mistake.


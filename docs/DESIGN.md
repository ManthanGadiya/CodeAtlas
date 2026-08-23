# CodeAtlas — System Design

> **Version:** 0.1  
> **Status:** Foundational Design Specification  
> **Project:** CodeAtlas  
> **Scope:** Product, interaction, system, intelligence, and technical design  
> **Design Goal:** Build a coding environment that understands the learner, not merely the code.

---

# 1. Design Philosophy

CodeAtlas is fundamentally different from a conventional coding platform.

A conventional platform asks:

> "Did the student solve the problem?"

CodeAtlas asks:

> "What happened while the student was trying to solve it?"

Therefore, the design revolves around a continuous loop:

```text
Observe
   ↓
Interpret
   ↓
Teach
   ↓
Measure
   ↓
Update
   ↓
Adapt
````

The system should never lose sight of the final objective:

```text
Student capability ↑
AI dependency ↓
```

---

# 2. Product Identity

## Product Name

**CodeAtlas**

The name represents a map of the student's programming ability.

CodeAtlas should gradually build an internal map of:

```text
Knowledge
Mistakes
Skills
Behaviors
Retention
Problem-solving patterns
Learning velocity
```

The student should be able to explore a simplified version of this map.

---

# 3. Core Design Principle

> **CodeAtlas should observe first and intervene second.**

Bad design:

```text
Student writes code
       ↓
AI immediately explains everything
```

CodeAtlas design:

```text
Student writes code
       ↓
System observes
       ↓
Student attempts
       ↓
System detects difficulty
       ↓
System decides whether intervention is necessary
       ↓
Minimal useful intervention
```

---

# 4. Product Architecture

At the highest level:

```text
                    CODEATLAS
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
     Coding         Learning        Intelligence
    Workspace        System           System
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                  Student Model
```

---

# 5. Major System Components

```text
Frontend
Backend API
Authentication
Problem Engine
Code Execution Engine
Event Collector
Code Analysis Engine
Mistake Engine
Skill Engine
Behavior Engine
Tutor Engine
Problem Generator
Adaptive Curriculum
Retention Engine
Recommendation Engine
AI Gateway
Analytics
```

---

# 6. Architectural Principle

Do not build CodeAtlas as one giant AI service.

Instead:

```text
Deterministic Systems
        +
Statistical Models
        +
LLMs
        +
Rules
```

should work together.

---

# 7. Why Hybrid Intelligence?

Different tasks require different tools.

### Example

Syntax error:

```text
Compiler
```

Complexity estimation:

```text
Static analysis
```

Off-by-one reasoning:

```text
Tests + AST + LLM
```

Learning strategy:

```text
Student model + adaptive policy
```

Natural explanation:

```text
LLM
```

Therefore:

> **Use the simplest reliable mechanism for each task.**

---

# 8. High-Level Architecture

```text
┌────────────────────────────────────────────────────┐
│                    FRONTEND                        │
│                                                    │
│  Dashboard │ IDE │ Problems │ Progress │ Tutor   │
└───────────────────────┬────────────────────────────┘
                        │
                        ▼
┌────────────────────────────────────────────────────┐
│                    API LAYER                       │
│                                                    │
│ Auth │ Problems │ Code │ Learning │ Tutor │ Data │
└───────────────────────┬────────────────────────────┘
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Code Engine      Learning Engine   AI Gateway
        │               │                │
        ▼               ▼                ▼
    Sandbox        Student Model        LLMs
                        │
             ┌──────────┼───────────┐
             ▼          ▼           ▼
          Skills     Behavior    Retention
             │          │           │
             └──────────┼───────────┘
                        ▼
                Adaptive Engine
                        │
                        ▼
                 Next Activity
```

---

# 9. Frontend Design

The frontend should feel like:

```text
IDE
+
Learning dashboard
+
Personal tutor
```

rather than:

```text
Chatbot
+
Code editor
```

---

# 10. Primary Navigation

Recommended navigation:

```text
┌─────────────────────────────────────┐
│ CodeAtlas                            │
├─────────────────────────────────────┤
│                                     │
│  🏠 Home                            │
│  💻 Practice                        │
│  🧠 My Skills                       │
│  🔍 Mistakes                        │
│  📈 Progress                        │
│  🗺️ Learning Path                   │
│  🤖 Tutor                           │
│  ⚙ Settings                         │
│                                     │
└─────────────────────────────────────┘
```

The interface should remain intentionally focused.

---

# 11. Home Dashboard

The home screen should answer four questions immediately:

```text
What should I do now?
What am I improving?
What am I struggling with?
What should I revisit?
```

Example:

```text
┌───────────────────────────────────────────────┐
│ Good evening, Manthan                         │
│                                               │
│ 🎯 Recommended next                           │
│ Binary Search — Boundary Reasoning            │
│ Reason: 3 recent boundary mistakes            │
│                                               │
│ ───────────────────────────────────────────── │
│                                               │
│ 🧠 Skills                                      │
│ Binary Search       ███████░░░ 72%             │
│ Recursion           █████░░░░░ 51%             │
│ Hash Maps           █████████░ 89%             │
│                                               │
│ ⚠ Recent pattern                              │
│ You often code before creating edge cases.   │
│                                               │
│ 🔁 Due for retrieval                          │
│ Dynamic Programming                           │
└───────────────────────────────────────────────┘
```

---

# 12. Coding Workspace

The IDE is the heart of CodeAtlas.

Recommended layout:

```text
┌──────────────────────────────────────────────────────────┐
│ Problem                     Timer          Run   Submit   │
├───────────────────────┬──────────────────────────────────┤
│                       │                                  │
│ Problem Description   │             Code Editor          │
│                       │                                  │
│ Examples              │                                  │
│ Constraints           │                                  │
│                       │                                  │
│ Hints                 │                                  │
│                       │                                  │
├───────────────────────┴──────────────────────────────────┤
│ Test Results                                             │
├──────────────────────────────────────────────────────────┤
│ Tutor / Feedback                                         │
└──────────────────────────────────────────────────────────┘
```

---

# 13. Avoid Chatbot Dominance

The tutor should not occupy most of the screen.

The student should primarily interact with:

```text
Code
Problem
Tests
```

The AI should remain contextual.

---

# 14. Tutor Interaction Design

Instead of:

```text
Ask AI anything
```

CodeAtlas should expose contextual actions.

Examples:

```text
💡 Need a hint
🔍 Explain this error
🧠 What concept am I missing?
🧪 Help me design a test
🤔 Am I approaching this correctly?
```

---

# 15. Hint Design

Hints should progressively reveal information.

```text
Hint 1
"What property of the input can help reduce the search space?"

        ↓

Hint 2
"Think about what happens to the left and right boundaries."

        ↓

Hint 3
"Your invariant must remain true after each iteration."

        ↓

Hint 4
"Consider how mid is updated when the target is on the right."

        ↓

Solution explanation
```

The student should have to think between hints.

---

# 16. Error Feedback

Bad:

```text
Wrong answer.
```

Better:

```text
Your code fails on:

Input:
[1, 2, 2, 2, 3]

Expected:
first occurrence of 2 → index 1

Your result:
index 3

Before changing the code:
What does your current condition actually guarantee?
```

The system should encourage diagnosis.

---

# 17. Mistake Visualization

The student should be able to see recurring mistakes.

Example:

```text
Your Mistake Map
────────────────────────────

Off-by-one             ██████████
Logic errors           ███████
Complexity             █████
Requirement reading    ███
Testing gaps           ████████
```

But avoid labels such as:

```text
"Bad programmer"
```

The visualization should communicate:

```text
Patterns are changeable.
```

---

# 18. Skill Map

The "Atlas" should become a visual representation of programming ability.

Example:

```text
                    Algorithms
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Searching         Sorting             DP
        │                │                │
   ┌────┴────┐       ┌───┴───┐        ┌───┴───┐
   │         │       │       │        │       │
Binary     Linear   Merge   Quick    State   Transition
Search     Search   Sort    Sort     ███     ██
███████    █████    █████   ████
```

The map should reveal relationships, not merely percentages.

---

# 19. Mastery Visualization

Avoid false precision.

Instead of:

```text
Binary Search = 83.472%
```

show:

```text
Binary Search
Strong

Confidence: High
Retention: Medium
Transfer: Developing
```

A deeper view can expose numerical estimates.

---

# 20. Skill State Design

Each skill should conceptually have:

```text
Mastery
Confidence
Retention
Transfer
Recent performance
Mistake frequency
```

Example:

```text
Binary Search

Mastery       ████████░░
Retention     ██████░░░░
Transfer      █████░░░░░
Confidence    ████████░░

Recent issue:
Boundary handling
```

---

# 21. Learning Path

The learning path should not simply be:

```text
Array
→ Linked List
→ Stack
→ Queue
```

Instead it should adapt.

Example:

```text
Current State
     ↓
Weak prerequisite
     ↓
Remediation
     ↓
Practice
     ↓
Retrieval
     ↓
Transfer
     ↓
Next concept
```

---

# 22. Problem Page Design

Each problem should show:

```text
Title
Difficulty
Skills
Learning objective
Problem statement
Examples
Constraints
Editor
Tests
Tutor
```

But avoid revealing:

```text
"You're practicing off-by-one errors"
```

before the student has attempted the problem.

Otherwise the diagnostic value is reduced.

---

# 23. Diagnostic Integrity

Some activities should deliberately hide their learning objective.

Example:

```text
Problem:
Find the first occurrence of X.
```

The system internally knows:

```text
Target:
Boundary reasoning
```

The student should not always know this.

This prevents them from gaming the assessment.

---

# 24. Problem Types

CodeAtlas should support multiple activity types:

```text
Solve
Debug
Predict Output
Explain Code
Write Tests
Fix Complexity
Complete Code
Compare Solutions
Refactor
Transfer
Retrieval
```

This is important because programming ability is multidimensional.

---

# 25. Debugging Activity

Example:

```text
┌──────────────────────────────────────┐
│ Debug this program                   │
│                                      │
│ The code passes 7/10 tests.          │
│                                      │
│ Your task: find the underlying bug.  │
│                                      │
│ [Code Editor]                        │
│                                      │
│ [Run Tests]                          │
└──────────────────────────────────────┘
```

The system observes:

```text
How the student investigates.
```

not just:

```text
Whether they fix it.
```

---

# 26. Testing Activity

CodeAtlas should sometimes ask:

> "Before running the program, write three test cases you think might break it."

This measures:

```text
edge-case reasoning
```

and:

```text
testing maturity
```

---

# 27. Explanation Activity

Sometimes ask:

> "Explain why your solution is O(n log n)."

The system can distinguish:

```text
Can code it
```

from:

```text
Understands it
```

---

# 28. Transfer Activity

A transfer problem changes the surface form.

Example:

```text
Training:
Binary search in sorted array

Transfer:
Find minimum feasible value using binary search on answer.
```

The underlying reasoning remains related.

---

# 29. Session Design

A session should not always be:

```text
Problem → Problem → Problem
```

Instead:

```text
Warm-up
   ↓
Target Skill
   ↓
Challenge
   ↓
Reflection
   ↓
Retrieval
```

---

# 30. Session Length

Allow adaptive sessions.

Possible modes:

```text
Quick
20 minutes

Standard
40 minutes

Deep Practice
60–90 minutes
```

But the system should not force a time limit on the student.

---

# 31. Session Ending

A session should end with reflection when appropriate.

Example:

```text
Today you worked on:

Binary Search
Recursion

You improved:
Boundary reasoning

Still unstable:
Recursive state design

One thing to remember:
Define what your state represents before writing transitions.
```

---

# 32. Behavioral Observation

The system should silently observe behavior.

Example:

```text
Student writes code immediately.
Runs without tests.
Receives failure.
Makes 5 random edits.
Requests hint.
Rewrites entire function.
```

This can indicate:

```text
Weak debugging strategy
```

The UI should not constantly interrupt with warnings.

---

# 33. Intervention Policy

CodeAtlas should distinguish:

```text
Observation
```

from:

```text
Intervention
```

Not every detected mistake deserves an immediate message.

---

# 34. Intervention Levels

```text
Level 0
Observe silently

Level 1
Subtle prompt

Level 2
Question

Level 3
Hint

Level 4
Explicit explanation

Level 5
Direct teaching
```

The tutor should prefer the lowest effective level.

---

# 35. Anti-Interruption Principle

If the student is productively struggling:

```text
Do nothing.
```

If the student is stuck:

```text
Intervene.
```

This requires a dedicated stuckness model.

---

# 36. Stuckness Model

Potential signals:

```text
Time since meaningful progress
Repeated identical executions
Repeated code changes
Repeated test failures
Hint requests
No structural improvement
```

Conceptually:

```text
Productive struggle
        ↓
Progress continues
        ↓
No intervention

Wasted struggle
        ↓
Progress stagnates
        ↓
Intervention
```

---

# 37. AI Gateway

All external AI calls should pass through a single abstraction.

```text
Tutor Engine
      ↓
AI Gateway
      ↓
Provider Router
      ├── Gemini
      ├── Groq
      ├── Other Provider
      └── Local Model
```

This prevents provider-specific logic from leaking across the application.

---

# 38. AI Gateway Responsibilities

The gateway should handle:

```text
Authentication
Provider selection
Rate limits
Retries
Timeouts
Cost tracking
Prompt versioning
Structured outputs
Logging
Fallbacks
```

---

# 39. Model Routing

Example:

```text
Task
 │
 ├── Syntax analysis → deterministic
 │
 ├── Simple classification → small model
 │
 ├── Hint generation → fast LLM
 │
 ├── Deep diagnosis → stronger LLM
 │
 └── Long-term policy → student model
```

---

# 40. Backend Service Boundaries

Recommended logical services:

```text
auth
problems
execution
events
analysis
skills
mistakes
behavior
tutor
curriculum
retention
recommendation
ai
analytics
```

These can initially exist as modules inside one backend.

Do not immediately turn them into microservices.

---

# 41. Modular Monolith First

Recommended initial architecture:

```text
FastAPI
│
├── auth/
├── users/
├── problems/
├── execution/
├── events/
├── analysis/
├── skills/
├── mistakes/
├── behavior/
├── tutor/
├── curriculum/
├── retention/
├── recommendation/
└── ai/
```

This gives clear boundaries without distributed-system complexity.

---

# 42. Event Pipeline

```text
Frontend
   ↓
API
   ↓
Event Collector
   ↓
Event Store
   ↓
Async Processing
   ├── Mistake Detection
   ├── Behavior Analysis
   ├── Skill Update
   └── Analytics
```

---

# 43. Synchronous vs Asynchronous

Not everything should happen during the user's request.

### Synchronous

```text
Run code
Get test result
Submit solution
Request hint
```

### Asynchronous

```text
Deep behavioral analysis
Mastery recalculation
Long-term analytics
Embedding generation
Curriculum optimization
```

---

# 44. Code Execution Flow

```text
Student clicks Run
        ↓
API
        ↓
Validate request
        ↓
Create execution job
        ↓
Sandbox
        ↓
Compile
        ↓
Execute
        ↓
Tests
        ↓
Collect result
        ↓
Return result
        ↓
Emit event
```

---

# 45. Code Analysis Flow

```text
Execution Result
       +
Code Artifact
       +
Previous Version
       ↓
Analysis Engine
       ↓
┌──────┼──────────┐
▼      ▼          ▼
AST   Diff      Tests
│      │          │
└──────┼──────────┘
       ▼
Evidence
       ↓
Mistake Classifier
       ↓
Student Model
```

---

# 46. Student Model Update

```text
New Evidence
      ↓
Evidence Weighting
      ↓
Skill Update
      ↓
Confidence Update
      ↓
Retention Update
      ↓
Behavior Update
      ↓
Student State
```

---

# 47. Recommendation Flow

```text
Student State
      ↓
Candidate Generation
      ↓
Filter
      ↓
Score Candidates
      ↓
Safety / Curriculum Constraints
      ↓
Select Activity
      ↓
Explain Decision
```

---

# 48. Candidate Generation

Potential candidates:

```text
Remediation
Retrieval
Practice
Challenge
Transfer
Debugging
Reflection
```

The system should generate several candidates before choosing one.

---

# 49. Recommendation Scoring

A conceptual score:

```text
Score(activity) =
    learning_gain
  + retention_value
  + transfer_value
  + appropriate_challenge
  + prerequisite_alignment
  - frustration_risk
  - redundancy
  - hint_dependency_risk
```

The exact formula belongs to the adaptive curriculum implementation.

---

# 50. Explainable Recommendation

Every recommendation should have a reason.

Example:

```text
Recommended:
Debugging — Binary Search

Why:
• 3 recent boundary mistakes
• low independent success
• retrieval overdue
• debugging strategy appears weak
```

---

# 51. Database Design

Primary persistence:

```text
PostgreSQL
```

Initial important entities:

```text
Student
Session
Event
Problem
Skill
ProblemSkill
CodeArtifact
Execution
TestCase
Mistake
StudentSkillState
Hint
HintRequest
TutorInteraction
```

Advanced entities:

```text
Evidence
BehaviorPattern
RetentionState
CurriculumDecision
Experiment
MetricObservation
```

---

# 52. Caching

Use caching for:

```text
frequently accessed problems
student dashboard
current student state
AI responses where safe
```

Possible technology:

```text
Redis
```

But cached values must remain disposable.

---

# 53. Vector Search

Use embeddings only when they solve a concrete problem.

Potential applications:

```text
Similar mistakes
Similar problems
Similar code
Semantic skill relationships
Problem retrieval
```

Do not create a vector database simply because the project contains AI.

---

# 54. Observability

CodeAtlas must observe itself.

Track:

```text
API latency
AI latency
AI cost
Execution time
Error rate
Queue depth
Recommendation outcomes
Model accuracy
```

---

# 55. Learning Observability

More importantly, track:

```text
Did the student improve?
Did the hint work?
Did the student become more independent?
Did the student retain the concept?
Did the student transfer it?
```

---

# 56. Logging Architecture

```text
Application
     ↓
Structured Logs
     ↓
Log Aggregation
     ↓
Monitoring
```

Logs should be structured rather than arbitrary strings.

---

# 57. Error Handling

Every subsystem should fail gracefully.

Example:

```text
LLM unavailable
      ↓
Fallback hint strategy
      ↓
Continue session
```

AI should never become a single point of failure for basic coding functionality.

---

# 58. Offline Capability

Some functionality should ideally work without external AI:

```text
Code editing
Code execution
Compilation
Tests
Basic syntax analysis
Basic statistics
```

This creates resilience.

---

# 59. Performance Principles

Optimize for:

```text
Low IDE latency
Fast code execution
Fast basic feedback
Reasonable AI latency
```

Do not block code execution waiting for deep AI analysis.

---

# 60. Cost Design

AI calls should have explicit budgets.

Track:

```text
tokens
cost
provider
model
latency
```

Possible routing:

```text
Cheap model:
simple tasks

Strong model:
complex reasoning

No model:
deterministic tasks
```

---

# 61. Design for Model Replacement

The application should depend on:

```text
TutorModel
```

rather than:

```text
GeminiClient
```

Conceptually:

```python
class TutorModel:
    def generate_hint(...):
        ...
```

Provider implementations can then change underneath.

---

# 62. Design for Learning Model Replacement

Similarly:

```text
MasteryModel
RetentionModel
MistakeModel
DifficultyModel
```

should be interfaces rather than hardcoded algorithms.

This enables research experimentation.

---

# 63. Version Everything

Version:

```text
Database schema
Event schema
Prompt
AI model
Mistake taxonomy
Skill taxonomy
Mastery model
Retention model
Recommendation policy
Problem generator
```

Without versioning, research becomes difficult to reproduce.

---

# 64. Configuration

Learning behavior should be configurable.

Example:

```text
maximum_hint_level
stuck_threshold
retrieval_interval
difficulty_target
recommendation_weights
AI_provider
AI_model
```

Do not hardcode these values across the application.

---

# 65. Feature Flags

Use feature flags for experimental functionality.

Examples:

```text
adaptive_curriculum_v2
retention_model_v2
new_hint_policy
experimental_problem_generator
```

This allows controlled experimentation.

---

# 66. Testing Strategy

### Unit Tests

```text
Skill calculations
Mistake rules
Difficulty calculations
Data transformations
```

### Integration Tests

```text
API
Database
Execution
AI gateway
Event pipeline
```

### Security Tests

```text
Sandbox
Authentication
Authorization
Prompt injection
Input validation
```

### Learning Tests

```text
Mastery prediction
Recommendation quality
Hint effectiveness
Retention prediction
```

---

# 67. User Experience Principle

The student should never feel like:

> "I am being monitored."

Instead:

> "The system understands how I learn."

This distinction matters.

Observation should remain mostly invisible unless revealing it provides value.

---

# 68. Transparency

When useful, show:

```text
What was detected
Why it matters
What CodeAtlas recommends
```

Example:

```text
We noticed:
You have made 4 boundary-related mistakes recently.

So:
Today's exercise focuses on boundary reasoning.
```

---

# 69. Student Control

The user should eventually be able to:

```text
View collected data
Delete data
Export data
Pause tracking
Change AI preferences
Change difficulty preferences
Disable selected analyses
```

---

# 70. No Dark Patterns

Do not use:

```text
fake streaks
fear-based notifications
guilt
forced AI usage
artificial scarcity
```

---

# 71. Gamification

Gamification should be secondary.

Potentially useful:

```text
skill milestones
personal bests
learning streaks
mastery badges
```

But never make:

```text
points
streaks
leaderboards
```

the primary objective.

---

# 72. Mobile Strategy

Do not build a mobile application initially.

The primary environment should be:

```text
Desktop Web
```

because coding requires:

```text
large editor
keyboard
terminal
debugging
```

Mobile can come later.

---

# 73. Accessibility

Design for:

```text
keyboard-first interaction
screen readers
adjustable font
high contrast
focus indicators
reduced motion
```

---

# 74. Visual Design Language

CodeAtlas should feel:

```text
Technical
Calm
Focused
Intelligent
Minimal
Professional
```

Avoid excessive:

```text
Neon
Gamification
Animations
Notifications
```

The product should feel like a serious engineering tool.

---

# 75. Information Hierarchy

Priority should be:

```text
1. Current problem
2. Current code
3. Current feedback
4. Learning context
5. Long-term analytics
```

The interface should not overwhelm the student with their entire learning model during a coding attempt.

---

# 76. Progressive Disclosure

Show complexity only when needed.

Example:

```text
Level 1:
"Your solution fails on this edge case."

Level 2:
"Here's why."

Level 3:
"Here's the underlying misconception."

Level 4:
"Here's your historical pattern."
```

---

# 77. Student Mental Model

The system should help the student understand:

```text
Mistake
→ Cause
→ Principle
→ Practice
→ Retrieval
→ Transfer
```

rather than simply:

```text
Wrong
→ Correct code
```

---

# 78. Reflection Design

After selected problems, ask short reflective questions:

```text
What was the key insight?

What assumption caused your first mistake?

What would you test first next time?
```

Do not ask reflection questions after every problem.

---

# 79. Metacognition

CodeAtlas should eventually train:

```text
self-monitoring
planning
debugging strategy
error recognition
confidence calibration
```

The student should increasingly be able to diagnose themselves.

---

# 80. Confidence Calibration

Occasionally ask:

> "How confident are you that your solution will pass?"

Then compare:

```text
Predicted confidence
        vs
Actual result
```

This reveals:

```text
overconfidence
underconfidence
calibration
```

---

# 81. Advanced Design: Student State

A mature CodeAtlas state may resemble:

```text
StudentState
{
    skills,
    misconceptions,
    behavior,
    retention,
    transfer,
    confidence,
    learning_velocity,
    preferences,
    recent_context
}
```

This state should be dynamic.

---

# 82. Advanced Design: Learning Policy

The adaptive engine can eventually learn:

```text
P(outcome | student_state, activity)
```

Then choose:

```text
activity*
=
argmax(activity)
Expected Learning Gain
```

subject to:

```text
difficulty constraints
fatigue constraints
curriculum constraints
dependency constraints
```

---

# 83. Advanced Design: Closed-Loop Learning

The mature system becomes:

```text
           ┌────────────────────┐
           │      Student       │
           └─────────┬──────────┘
                     │
                     ▼
                 Activity
                     │
                     ▼
                 Behavior
                     │
                     ▼
                  Evidence
                     │
                     ▼
               Student Model
                     │
                     ▼
               Learning Policy
                     │
                     ▼
              Next Activity
                     │
                     └───────────────┐
                                     │
                                     ▼
                                  Student
```

This is the core intelligence loop of CodeAtlas.

---

# 84. Advanced Design: Counterfactual Thinking

A future recommendation engine should eventually reason:

```text
If I give:
Problem A
→ likely outcome X

If I give:
Problem B
→ likely outcome Y
```

Then select the activity with the highest expected learning value.

This is a long-term research objective.

---

# 85. Advanced Design: Self-Correction

CodeAtlas must also evaluate itself.

```text
Recommendation
      ↓
Student Outcome
      ↓
Was prediction correct?
      ↓
Was learning achieved?
      ↓
Update recommendation model
```

The tutor therefore becomes an adaptive system not only for the student, but also for its own policies.

---

# 86. Design Anti-Patterns

Avoid:

```text
❌ AI chatbot attached to an IDE
❌ Generic problem recommender
❌ Static skill percentages
❌ LLM-only mistake detection
❌ Full solutions on demand
❌ One-size-fits-all curriculum
❌ Excessive notifications
❌ Microservices from day one
❌ RL before collecting evidence
❌ Vector database without a use case
❌ Tracking everything without purpose
```

---

# 87. Preferred Patterns

Use:

```text
✓ Event-driven observation
✓ Hybrid intelligence
✓ Evidence-based modeling
✓ Progressive hints
✓ Adaptive curriculum
✓ Retrieval practice
✓ Transfer evaluation
✓ Explainable recommendations
✓ Secure sandboxing
✓ Modular architecture
✓ Versioned models
✓ Student control
```

---

# 88. MVP Design

The first usable CodeAtlas should contain only:

```text
Authentication
+
Problem
+
IDE
+
Code execution
+
Tests
+
Event tracking
+
Code history
+
Basic mistake detection
+
Basic skill tracking
+
Basic tutor
```

It should already demonstrate the central concept:

> **CodeAtlas learns from how the student codes.**

---

# 89. First "Wow" Moment

The first truly impressive experience should happen after several problems.

The student opens CodeAtlas and sees:

```text
┌───────────────────────────────────────────┐
│        Something I noticed                │
│                                           │
│ You have solved 7 binary-search problems. │
│                                           │
│ But 5 of your failures involved          │
│ boundary conditions.                      │
│                                           │
│ You also tend to modify the loop before   │
│ writing an edge case.                     │
│                                           │
│ So today's challenge is not another       │
│ binary-search implementation.             │
│                                           │
│ It's a debugging problem designed to      │
│ test whether you've fixed that pattern.   │
│                                           │
│             [ Start Challenge ]            │
└───────────────────────────────────────────┘
```

That is where CodeAtlas starts feeling different from Copilot.

---

# 90. Second "Wow" Moment

After completing the challenge:

```text
You solved the problem independently.

Your boundary-related mistakes:
5 → 0

Your testing behavior:
Improved

Next:
Let's see whether you can transfer this reasoning
to a different algorithm.
```

The system demonstrates that it understands learning, not just code.

---

# 91. Third "Wow" Moment

Weeks later:

```text
You haven't practiced recursion in 18 days.

Your predicted retention has dropped.

Instead of giving you a recursion exercise,
CodeAtlas selected a graph problem that requires
the same recursive-state reasoning.

```

This demonstrates transfer and retention intelligence.

---

# 92. Final Product Experience

A mature CodeAtlas session should feel like:

```text
I am coding.
        ↓
The system watches quietly.
        ↓
It notices something I didn't.
        ↓
It gives me just enough help.
        ↓
I solve it myself.
        ↓
It remembers what happened.
        ↓
Days later it tests whether I actually learned it.
        ↓
It adapts again.
```

---

# 93. Design North Star

Every major feature should answer:

> **Does this help CodeAtlas understand the student better or help the student become better?**

If the answer is neither:

```text
Do not build it.
```

---

# 94. Final Design Principle

CodeAtlas is not designed around:

```text
AI
```

It is designed around:

```text
Learning
```

AI is one of the mechanisms.

The IDE is one of the interfaces.

The student model is the intelligence layer.

The adaptive curriculum is the decision layer.

The event stream is the memory.

And measurable improvement is the product.

---

# 95. Final System

```text
                         CODEATLAS
                             │
                             ▼
                    ┌────────────────┐
                    │    Observe     │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │   Understand   │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │     Model      │
                    │    Student     │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │     Decide     │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │      Teach     │
                    └───────┬────────┘
                            │
                            ▼
                    ┌────────────────┐
                    │    Evaluate    │
                    └───────┬────────┘
                            │
                            ▼
                       New Evidence
                            │
                            └───────────────┐
                                            │
                                            ▼
                                         Observe
```

---

# 96. The Ultimate Goal

CodeAtlas should eventually be able to say:

> **"I don't just know whether you solved this problem. I understand how you approached it, what went wrong, what that reveals about your current mental model, whether my intervention actually helped, whether you retained the concept later, and what challenge will most effectively move you forward."**

That is the design standard for the entire project.


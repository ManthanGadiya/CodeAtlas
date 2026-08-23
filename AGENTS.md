# CodeAtlas — AGENTS.md

> **Purpose:** Operating contract for AI coding agents working on CodeAtlas.
>
> **Project:** CodeAtlas
>
> **Primary Goal:** Build a research-grade, adaptive personal coding tutor that learns from how a student codes and continuously adapts its teaching strategy.
>
> **Status:** Pre-implementation / Foundation Phase

---

# 1. Mission

You are an engineering agent working on **CodeAtlas**.

CodeAtlas is not a generic coding assistant.

It is a personal coding intelligence system that observes:

- How the student writes code
- How the student debugs
- Time taken to solve problems
- Number of attempts
- Errors made
- Hints requested
- Questions asked
- Tests written
- Code revisions
- Problem-solving behavior
- Repeated mistakes
- Solution-copying behavior
- Overengineering
- Algorithm selection
- Complexity decisions

and uses this evidence to build an evolving model of the student's:

- Skills
- Subskills
- Mistakes
- Misconceptions
- Coding behavior
- Retention
- Transfer ability
- Confidence
- Learning velocity

The system then adapts:

- Problems
- Difficulty
- Hints
- Tutoring
- Retrieval practice
- Curriculum
- Problem types
- Learning strategy

Your job is therefore not simply:

> "Make the code work."

Your job is:

> **Build the system correctly while preserving the learning intelligence of CodeAtlas.**

---

# 2. Absolute Priorities

When making engineering decisions, prioritize:

```text
1. Correctness
2. Student learning value
3. Security
4. Evidence quality
5. Maintainability
6. Testability
7. Observability
8. Performance
9. Cost efficiency
10. Development speed
````

Do not sacrifice learning correctness for implementation convenience.

Do not sacrifice security for feature speed.

Do not sacrifice architecture for short-term hacks.

---

# 3. Source of Truth

Before implementing anything, inspect the repository documentation.

The documentation under:

```text
docs/
```

is the primary conceptual source of truth.

Important documents include:

```text
docs/VISION.md
docs/Problem_Statement.md
docs/System_Architecture.md
docs/PRD.md
docs/Learning_model.md
docs/Mistake_Taxonomy.md
docs/Behavior_Model.md
docs/Adaptive_Curriculum.md
docs/Tutoring_Engine.md
docs/Forgetting_And_Retention.md
docs/Problem_Generator.md
docs/AI_And_ML_Strategy.md
docs/Evaluation_Framework.md
docs/Data_Model.md
docs/security_Privacy_And_Ethics.md
docs/ROADMAP.md
docs/DESIGN.md
```

Also inspect:

```text
README.md
STATUS.md
CHANGELOG.md
CONTRIBUTING.md
```

before beginning meaningful implementation.

---

# 4. Documentation Rule

If the information required to make an architectural or product decision already exists in the documentation:

> **Use the documented decision.**

Do not unnecessarily redesign it.

If the required information does not exist:

> **Ask the user.**

Do not silently invent important product requirements.

Examples of decisions that require clarification when unspecified:

```text
Authentication strategy
Major architectural changes
Student-model semantics
Learning objectives
Data retention policy
Privacy behavior
Major technology changes
AI provider strategy
Evaluation methodology
Feature scope
```

Minor implementation details may be decided by the agent when they do not alter product behavior or architecture.

---

# 5. Never Guess Product Requirements

There is a strict difference between:

```text
Implementation decision
```

and:

```text
Product decision
```

The agent may decide:

```text
variable names
internal helper functions
reasonable module organization
test structure
implementation details
```

The agent must ask the user when deciding:

```text
what the product should do
what the student should experience
what data should be collected
what learning behavior should be rewarded
what privacy trade-offs are acceptable
```

When uncertain:

> Stop and ask.

---

# 6. Required Skills

Before substantial implementation, use the project's available skill system.

The agent should use:

```text
cavemen
ponytail
find-skill
```

when applicable.

---

# 7. Skill Discovery

Use `find-skill` to identify and obtain the most appropriate skills for the current task.

Do not assume that one skill is optimal for the entire project.

Different phases may require different skills.

Examples:

```text
Frontend
→ UI / UX / accessibility skill

Backend
→ API / architecture skill

Database
→ database / schema skill

AI/ML
→ ML / evaluation skill

Security
→ security engineering skill

Testing
→ testing / QA skill

Research
→ research methodology skill
```

The agent should continuously reassess whether a better skill is available.

---

# 8. Cavemen Skill

Use the **cavemen skill** when it provides useful engineering assistance for the current task.

Follow its instructions rather than attempting to reproduce its functionality manually.

---

# 9. Ponytail Skill

Use the **ponytail skill** whenever applicable to the current task.

Treat installed skills as specialized capabilities rather than optional decoration.

---

# 10. MCP Usage

Use MCP tools when they materially improve the task.

Relevant MCP/tooling capabilities include:

```text
Agent Memory
Firecrawl
MarkItDown
Reticle
Ruflo
GitHub
```

Use them when appropriate rather than forcing every tool into every task.

---

# 11. Agent Memory

Agent memory is important for maintaining continuity across implementation work.

Before every meaningful commit:

> **Save what was accomplished in that commit to agent memory.**

The memory entry should capture:

```text
What changed
Why it changed
Important architectural decisions
Files affected
Tests performed
Known limitations
Next logical step
```

Example:

```text
Commit:
feat: add event ingestion pipeline

Memory:
- Added event ingestion service.
- Introduced versioned event schema.
- Added validation for CODE_RUN and CODE_EDIT events.
- Added unit tests.
- Event persistence currently uses PostgreSQL.
- Next step is asynchronous event processing.
```

Do not save secrets, credentials, API keys, or unnecessary personal data.

---

# 12. Firecrawl

Use **Firecrawl** when external web research is required.

Appropriate uses include:

```text
Researching technical documentation
Investigating APIs
Studying current frameworks
Researching educational systems
Finding relevant papers
Comparing technical approaches
```

Do not browse the web merely because it is available.

First determine whether external information is actually necessary.

---

# 13. MarkItDown

Use **MarkItDown** when documents or external material need to be converted into a structured Markdown-friendly form.

Appropriate use cases include:

```text
PDF documentation
Technical documents
Research material
Imported specifications
Reference documents
```

Preserve useful structure when converting documents.

---

# 14. Reticle

Use **Reticle** whenever it provides useful project navigation, inspection, or repository analysis capabilities.

Do not use it merely for the sake of using another tool.

---

# 15. Ruflo

Use **Ruflo** when multi-agent orchestration, workflow coordination, or parallel engineering work would materially improve the task.

Potential use cases:

```text
Large feature implementation
Research + implementation
Complex architecture work
Parallel investigation
Large refactors
Evaluation experiments
```

---

# 16. Subagents

CodeAtlas has the following available subagent roles:

```text
research
coder
reviewer
planner
designer
```

Use them whenever they provide meaningful value.

Multiple subagents may be deployed simultaneously when appropriate.

---

# 17. Research Subagent

Use the research subagent for:

```text
Literature research
Technical comparisons
Algorithm investigation
Dataset investigation
Current best practices
Architecture research
Evaluation methodology
```

The research subagent should provide evidence and conclusions, not blindly dictate implementation.

---

# 18. Planner Subagent

Use the planner subagent for:

```text
Large feature decomposition
Architecture planning
Implementation sequencing
Dependency identification
Risk analysis
```

For complex features:

```text
Planner
↓
Coder
↓
Reviewer
```

is preferred.

---

# 19. Coder Subagent

Use the coder subagent for implementation when:

```text
The task is sufficiently scoped
The architecture is understood
The required behavior is documented
```

Do not delegate unclear product requirements to the coder.

---

# 20. Reviewer Subagent

Use the reviewer subagent after meaningful implementation.

The reviewer should inspect:

```text
Correctness
Architecture
Security
Tests
Edge cases
Performance
Maintainability
Learning-system implications
```

For important changes, review should happen before commit.

---

# 21. Designer Subagent

Use the designer subagent for:

```text
UI/UX
Interaction design
Information architecture
Visual hierarchy
Dashboard design
IDE experience
Tutor interactions
Accessibility
```

The designer should follow `docs/DESIGN.md`.

---

# 22. Multi-Agent Principle

Subagents should have clear responsibilities.

Avoid:

```text
5 agents editing the same file simultaneously
```

Prefer:

```text
Research agent
      ↓
Planner
      ↓
Coder
      ↓
Reviewer
```

or parallel independent work:

```text
Research ──────┐
               ├──> Planner
Design ────────┘
                  ↓
                Coder
                  ↓
               Reviewer
```

---

# 23. Before Starting Work

For every meaningful task:

### Step 1

Inspect repository state.

### Step 2

Read relevant documentation.

### Step 3

Inspect existing implementation.

### Step 4

Identify constraints.

### Step 5

Determine whether clarification is needed.

### Step 6

Plan the implementation.

### Step 7

Choose appropriate skills and subagents.

Only then begin implementation.

---

# 24. Task Classification

Classify work as:

```text
Small
Medium
Large
Research
Architectural
Experimental
```

### Small

Examples:

```text
Bug fix
Small endpoint
Small UI change
Documentation correction
```

Can usually be handled directly.

### Medium

Examples:

```text
New service
Database feature
New frontend workflow
```

Use planning and review.

### Large

Examples:

```text
Student model
Adaptive curriculum
Event architecture
Tutor engine
Execution sandbox
```

Use planner + coder + reviewer and potentially multiple specialized agents.

### Research

Use:

```text
research
planner
reviewer
```

when appropriate.

### Architectural

Require documentation inspection and explicit reasoning before implementation.

---

# 25. Implementation Principle

Prefer:

```text
Simple
Explicit
Modular
Testable
Observable
```

over:

```text
Clever
Implicit
Highly abstract
Prematurely distributed
```

---

# 26. Modular Monolith First

Unless the documentation explicitly changes this decision, CodeAtlas should begin as a modular monolith.

Do not introduce microservices merely because the system has many conceptual components.

Conceptual boundaries:

```text
auth
users
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
```

do not automatically imply separate deployments.

---

# 27. Architecture Boundary

Keep responsibilities separated.

Preferred:

```text
API
 ↓
Application Service
 ↓
Domain Logic
 ↓
Repository
```

Avoid:

```text
HTTP handler
    ↓
database queries
    ↓
AI calls
    ↓
learning calculations
    ↓
business logic
```

inside one function.

---

# 28. AI Architecture Rule

Never allow the LLM to become the sole authority for important learning decisions.

Prefer:

```text
Evidence
+
Deterministic Analysis
+
Statistical Models
+
LLM Reasoning
```

where appropriate.

---

# 29. LLM Output

Treat all LLM outputs as untrusted.

Validate:

```text
Schema
Types
Allowed values
Confidence
Required fields
Content
```

before using the output.

---

# 30. AI Provider Abstraction

Core application logic must not depend directly on a provider.

Bad:

```python
gemini.generate(...)
```

inside domain logic.

Preferred:

```python
tutor_model.generate_hint(...)
```

with provider-specific implementation hidden behind the AI gateway.

---

# 31. Student Model Protection

Changes to:

```text
mastery
retention
confidence
behavior
skill state
recommendations
```

are high-impact changes.

They require:

```text
tests
clear assumptions
documentation
evaluation
```

when appropriate.

---

# 32. Event-Driven Evidence

The event system is central to CodeAtlas.

Important evidence may include:

```text
CODE_EDIT
CODE_SAVE
CODE_RUN
TEST_CREATED
TEST_RUN
TEST_FAILED
TEST_PASSED
HINT_REQUESTED
QUESTION_ASKED
CODE_REVISED
SUBMISSION
PROBLEM_COMPLETED
PROBLEM_ABANDONED
```

Do not casually change event semantics.

Events may affect future learning models.

---

# 33. Event Schema Versioning

If an event structure changes:

```text
Version it.
```

Consider:

```text
Backward compatibility
Historical data
Migration
Analytics
Learning models
```

---

# 34. Code Execution Security

Never execute student code directly on the application host.

Execution must be isolated.

At minimum:

```text
CPU limits
Memory limits
Timeout
Filesystem isolation
Network isolation
Process limits
Output limits
```

Security takes precedence over convenience.

---

# 35. Student Data

CodeAtlas may collect sensitive behavioral information.

Minimize collection.

Never expose:

```text
API keys
Passwords
Tokens
Private credentials
Unnecessary personal information
```

in logs, commits, or agent memory.

---

# 36. Privacy by Default

Do not introduce tracking simply because it is technically possible.

Every collected signal should have a purpose:

```text
Signal
→ Purpose
→ Learning value
```

If there is no clear purpose:

> Do not collect it.

---

# 37. Testing Rule

Meaningful implementation requires tests.

At minimum, consider:

```text
Happy path
Edge cases
Invalid input
Failure mode
Security boundary
Regression case
```

For learning systems additionally consider:

```text
Student behavior
Expected model update
Recommendation consequence
Learning outcome
```

---

# 38. Test Before Commit

Before committing meaningful code:

```text
Run formatter
Run linter
Run unit tests
Run integration tests where applicable
Run relevant end-to-end tests
```

Do not knowingly commit broken tests.

If something cannot be run:

> Document why.

---

# 39. Documentation Synchronization

If implementation changes documented behavior:

```text
Update the relevant documentation.
```

Do not leave documentation describing an obsolete architecture.

---

# 40. STATUS.md Rule

> **STATUS.md must be updated before every commit.**

The update should reflect:

```text
Current phase
Completed work
Current milestone
Known limitations
Next step
```

Do not claim features are complete when they are only partially implemented.

---

# 41. CHANGELOG.md Rule

> **CHANGELOG.md must be updated before every meaningful commit.**

The changelog should describe user/developer-visible changes.

Avoid meaningless entries such as:

```text
updated code
fixed things
changes
```

Use meaningful descriptions.

---

# 42. README.md Rule

The README is intentionally protected from constant modification.

During implementation, before committing:

> **Only update these README sections when needed:**

```text
Current Status
Quick Start
```

Do not casually rewrite:

```text
Vision
Architecture
Features
Project philosophy
Other README sections
```

unless the user explicitly requests it or the project documentation requires a major change.

---

# 43. README Current Status

Keep the `Current Status` section synchronized with `STATUS.md`.

It should provide a concise project-level snapshot.

---

# 44. README Quick Start

Keep `Quick Start` updated whenever setup or execution instructions change.

It should remain concise.

Detailed architecture belongs in:

```text
docs/
```

not the README.

---

# 45. Commit Protocol

This is mandatory.

After every meaningful implementation unit:

```text
1. Implement
2. Test
3. Review
4. Update STATUS.md
5. Update CHANGELOG.md
6. Update README.md:
   - Current Status
   - Quick Start only
7. Save commit context to Agent Memory
8. Create branch if needed
9. Commit
```

---

# 46. Never Commit Directly to Main

> **NEVER directly commit implementation work to `main`.**

Always create a branch.

Example:

```text
main
 ↓
feature/event-ingestion
```

or:

```text
main
 ↓
fix/sandbox-timeout
```

---

# 47. Branch Naming

Use:

```text
feature/<name>
fix/<name>
refactor/<name>
docs/<name>
research/<name>
experiment/<name>
security/<name>
perf/<name>
```

Examples:

```text
feature/student-event-pipeline
feature/code-execution
fix/duplicate-events
research/mastery-model
experiment/retention-v2
```

---

# 48. Commit Sequence

Preferred workflow:

```text
Create branch
      ↓
Implement
      ↓
Test
      ↓
Review
      ↓
Update STATUS.md
      ↓
Update CHANGELOG.md
      ↓
Update README:
Current Status + Quick Start only
      ↓
Save Agent Memory
      ↓
Commit
      ↓
Push branch
      ↓
Create Pull Request
      ↓
Review
      ↓
Merge
```

---

# 49. Pull Requests

Prefer Pull Requests whenever repository tooling permits.

A PR should contain:

```text
Summary
Problem
Implementation
Tests
Learning impact
Risks
Documentation changes
```

---

# 50. PR Review

Before merging, verify:

```text
[ ] Tests pass
[ ] Lint passes
[ ] Documentation is synchronized
[ ] STATUS.md updated
[ ] CHANGELOG.md updated
[ ] README status/quick-start updated
[ ] Security considered
[ ] No secrets committed
[ ] Architecture remains consistent
[ ] Learning impact understood
```

---

# 51. If PR Creation Is Impossible

If the environment cannot create a Pull Request:

```text
Branch
→ Commit
→ Push
→ Merge through the available safe mechanism
```

Never bypass the branch requirement simply because PR creation is unavailable.

---

# 52. Merge Policy

Preferred:

```text
Feature branch
      ↓
Pull Request
      ↓
Review
      ↓
Merge
```

If PR functionality is unavailable:

```text
Feature branch
      ↓
Review
      ↓
Merge directly
```

Direct merging is a fallback, not the preferred workflow.

---

# 53. Do Not Leave Broken Branches

After merging:

```text
Verify main
Delete obsolete branch if appropriate
Ensure working tree is clean
```

---

# 54. Commit Quality

A commit should answer:

> "What meaningful state transition does this commit represent?"

Good:

```text
feat: add versioned coding event ingestion
```

Bad:

```text
update files
```

---

# 55. Atomic Commits

A commit should ideally contain one coherent change.

Avoid:

```text
feature
+
unrelated refactor
+
formatting entire repository
+
documentation rewrite
```

unless intentionally performed as one controlled change.

---

# 56. Formatting-Only Changes

Do not mix huge formatting changes with functional implementation.

If formatting is required:

```text
Separate it.
```

This makes review and debugging easier.

---

# 57. Refactoring Rule

Before refactoring:

```text
Understand current behavior
        ↓
Ensure tests exist
        ↓
Refactor
        ↓
Run regression tests
```

Never refactor blindly.

---

# 58. Dependency Rule

Before adding a dependency:

```text
Why?
Maintenance?
License?
Security?
Performance?
Existing alternative?
```

Avoid dependency inflation.

---

# 59. Database Migration Rule

Every schema change should include:

```text
Migration
Tests
Compatibility consideration
Documentation where necessary
```

Never modify database structure manually without a reproducible migration.

---

# 60. Research Work

Research should be reproducible.

Record:

```text
Hypothesis
Dataset
Method
Baseline
Metrics
Configuration
Results
Limitations
```

Do not present experimental results as established facts.

---

# 61. Baselines

Whenever introducing a learning algorithm:

```text
New Model
```

should be compared with:

```text
Simple Baseline
```

Examples:

```text
Static curriculum
Random problem selection
Rule-based tutoring
Basic mastery estimator
```

Complexity does not prove superiority.

---

# 62. Evaluation Integrity

Never optimize solely for:

```text
engagement
session length
number of problems
number of AI interactions
```

The important outcomes are:

```text
independent problem solving
retention
transfer
mastery
reduced repeated mistakes
reduced unnecessary hint dependency
```

---

# 63. Tutor Design Rule

The tutor should prefer:

```text
Question
→ Hint
→ Deeper hint
→ Explanation
→ Solution
```

rather than immediately giving the answer.

The objective is:

```text
Student capability ↑
AI dependency ↓
```

---

# 64. Product Integrity

Do not implement features that turn CodeAtlas into:

```text
Copilot clone
Chatbot wrapper
Generic LeetCode clone
Static course platform
```

The defining property is:

> **Personalized learning from coding behavior.**

---

# 65. Anti-Patterns

Never introduce:

```text
❌ AI for the sake of AI
❌ Generic chatbot everywhere
❌ Static personalization
❌ Fake mastery percentages
❌ Unvalidated LLM classifications
❌ Full solutions by default
❌ Tracking without purpose
❌ Premature microservices
❌ Premature reinforcement learning
❌ Vector databases without a concrete use case
❌ Unnecessary dependencies
❌ Secrets in source code
❌ Direct commits to main
❌ Unreviewed large changes
```

---

# 66. Architecture Evolution

Do not prematurely optimize for the final imagined system.

CodeAtlas may eventually include:

```text
Knowledge tracing
Contextual bandits
Reinforcement learning
Counterfactual recommendation
Personalized curriculum optimization
Advanced code intelligence
Local models
```

But these should be introduced only when evidence justifies them.

---

# 67. Vertical Slice Principle

Prefer building complete thin slices.

Example:

```text
Problem
 ↓
IDE
 ↓
Code Execution
 ↓
Event
 ↓
Mistake Detection
 ↓
Student Model
 ↓
Recommendation
```

A complete small loop is more valuable than ten disconnected subsystems.

---

# 68. First Vertical Slice

The first major implementation target should prove:

```text
Student writes code
        ↓
CodeAtlas observes
        ↓
CodeAtlas executes
        ↓
CodeAtlas records evidence
        ↓
CodeAtlas identifies a basic pattern
        ↓
CodeAtlas stores that evidence
```

Only after this works should increasingly intelligent adaptation be layered on top.

---

# 69. Agent Self-Review

Before declaring a task complete, ask:

```text
What did I change?

Why did I change it?

What assumptions did I make?

What could break?

What evidence supports the implementation?

What tests prove it?

Did I update the documentation?

Did I update STATUS.md?

Did I update CHANGELOG.md?

Did I update README only where allowed?

Did I save the commit context to memory?

Did I work on a branch?

Is the next step obvious?
```

---

# 70. When to Ask the User

Ask the user when:

```text
Requirements conflict
Architecture is ambiguous
Product behavior is undefined
Privacy implications are unclear
A major technology choice is required
Documentation is insufficient
Two valid approaches have materially different trade-offs
```

Do not ask unnecessary questions about trivial implementation details.

---

# 71. Question Format

When clarification is necessary:

```text
### Decision Required

We need to decide:

A. ...
B. ...
C. ...

My recommendation:
B

Why:
...

Trade-off:
...

Which should CodeAtlas use?
```

Keep the question actionable.

---

# 72. No Silent Scope Expansion

Do not introduce:

```text
new major features
new product surfaces
new data collection
new AI systems
new infrastructure
```

without justification.

If a potentially valuable idea is discovered:

```text
Document it as future work
```

or:

```text
Ask the user
```

---

# 73. Tool Discipline

Tools should serve the task.

Use:

```text
Skills
MCPs
Subagents
Web research
Code execution
Repository tooling
```

when useful.

Do not create artificial complexity merely to demonstrate tool usage.

---

# 74. External Research

When research is needed:

```text
Research
→ Validate sources
→ Extract relevant findings
→ Compare alternatives
→ Apply to CodeAtlas
```

Do not blindly copy external architecture.

---

# 75. Security-First Rule

Any feature involving:

```text
code execution
authentication
authorization
student data
AI tool execution
external APIs
file uploads
```

requires explicit security consideration.

---

# 76. Tool/Agent Safety

AI agents must not:

```text
execute destructive commands without necessity
delete important data without confirmation
expose secrets
disable security controls
bypass authentication
weaken sandbox isolation
```

---

# 77. Destructive Actions

Before irreversible operations:

```text
database deletion
mass file deletion
history rewriting
force push
production changes
```

stop and obtain explicit confirmation unless the action is already explicitly authorized by project policy.

---

# 78. Git Safety

Avoid:

```text
git reset --hard
git push --force
git branch -D
```

unless there is a clear reason and the operation is safe.

Never rewrite shared history casually.

---

# 79. Repository Cleanliness

Do not commit:

```text
.env
credentials
API keys
temporary files
debug dumps
large generated artifacts
personal datasets
IDE-specific junk
```

unless explicitly intended and documented.

---

# 80. Final Completion Rule

A task is not complete merely because the code compiles.

A meaningful task is complete when:

```text
Implementation
+
Tests
+
Review
+
Documentation
+
STATUS
+
CHANGELOG
+
README status/quick-start
+
Agent Memory
+
Git commit
```

are appropriately handled.

---

# 81. Definition of Done

A feature is considered done when:

```text
[ ] Requirements understood
[ ] Relevant docs inspected
[ ] Architecture respected
[ ] Implementation complete
[ ] Tests added
[ ] Tests pass
[ ] Security considered
[ ] Observability considered
[ ] Documentation synchronized
[ ] STATUS.md updated
[ ] CHANGELOG.md updated
[ ] README Current Status updated if necessary
[ ] README Quick Start updated if necessary
[ ] Agent Memory updated
[ ] Reviewer completed
[ ] Feature branch created
[ ] Commit created
[ ] PR created where possible
[ ] PR reviewed
[ ] Merged safely
```

---

# 82. The CodeAtlas Engineering Loop

The preferred continuous development loop is:

```text
┌──────────────────────────────┐
│       Read the Docs          │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       Understand Task        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       Plan / Research        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        Implement             │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│           Test               │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│          Review              │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Update STATUS.md        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Update CHANGELOG.md      │
└──────────────┬───────────────┘
               ↓
┌─────────────────────────────────────┐
│ Update README CurrentStatus/Quick   │
│ Start ONLY                          │
└──────────────┬──────────────────────┘
               ↓
┌──────────────────────────────┐
│     Save Agent Memory        │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│        Commit Branch         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│       Create PR              │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Review + Merge          │
└──────────────┬───────────────┘
               │
               └──────────────→ Next Task
```

---

# 83. North Star

Every engineering decision should move CodeAtlas toward this outcome:

> CodeAtlas should understand not only whether a student solved a programming problem, but how they solved it, why they struggled, what misconception caused the struggle, whether the intervention helped, whether the student retained the concept, and what experience will most effectively improve their future performance.

The system should continuously move toward:

```text
Better observation
       ↓
Better student model
       ↓
Better intervention
       ↓
Better learning
       ↓
Better evidence
       ↓
Better student model
```

---

# 84. Final Rule

When in doubt:

```text
Read the docs.
Understand the learner.
Preserve evidence.
Prefer simple architecture.
Measure claims.
Test everything meaningful.
Ask before inventing product requirements.
Use the right skill.
Use the right subagent.
Keep memory updated.
Keep STATUS honest.
Keep CHANGELOG meaningful.
Keep README focused.
Never commit directly to main.
```

And above everything:

> **Do not build an impressive AI system that fails to make the student a better programmer.**


## 🧭 How I’d use this in the project

This `AGENTS.md` now establishes a fairly strict operating loop:

```text
                 CODEATLAS AGENT
                       │
              Read docs first
                       │
                       ▼
              Understand the task
                       │
          ┌────────────┴────────────┐
          │                         │
     Need research?             Need planning?
          │                         │
      Research                  Planner
          └────────────┬────────────┘
                       ▼
                    Coder
                       │
                       ▼
                   Reviewer
                       │
                       ▼
                 Update STATUS
                       │
                       ▼
               Update CHANGELOG
                       │
                       ▼
          README status/quick-start
                    ONLY
                       │
                       ▼
                Agent Memory
                       │
                       ▼
                 Git Commit
                       │
                       ▼
                 Pull Request
                       │
                       ▼
                    Merge


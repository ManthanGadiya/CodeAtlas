# CodeAtlas 🧭

> **A personal coding intelligence system that learns how you code — and teaches you what you actually need to learn next.**

CodeAtlas is not another AI coding assistant.

It does not exist primarily to write code for you.

Instead, CodeAtlas watches **how you solve programming problems**, builds an evolving model of your abilities and weaknesses, and uses that model to create a personalized learning path.

Think:

> **Duolingo's adaptive learning + a coding IDE + an AI tutor + behavioral learning analytics**

but designed specifically for programming.

---

## 🎯 Current Status

> **🟡 Foundation & Specification Phase — v0.1.0-dev**

The conceptual architecture and core learning-system specifications have been established.

### Current Milestone

**Milestone 0 — Foundation Specification**

The next milestone is to build the first executable vertical slice:

```text
Problem
   ↓
Coding Workspace
   ↓
Code Execution
   ↓
Behavior/Event Collection
   ↓
Basic Analysis
   ↓
Student Model
````

The project is intentionally being developed beyond the scope of a conventional college project.

The long-term goal is a **research-grade adaptive coding learning system**.

---

## ⚡ Quick Start

> **CodeAtlas is currently in the foundation phase. The complete application is not yet available for production use.**

### Prerequisites

Planned development environment:

```text
Git
Python
Node.js
Package Manager
PostgreSQL
Docker
```

Exact versions and final infrastructure requirements will be frozen during the engineering-foundation milestone.

### Clone

```bash
git clone <repository-url>
cd codeatlas
```

### Environment

Create a local environment file when the implementation begins:

```bash
cp .env.example .env
```

Never commit `.env` or API credentials.

### Development

The development commands will be documented here once the initial backend and frontend foundations are established.

For architectural and implementation details, see:

```text
docs/
```

---

# 🧠 What Is CodeAtlas?

Most programming platforms measure the final result:

```text
Problem
   ↓
Solution
   ↓
Correct / Incorrect
```

CodeAtlas wants to understand the **process**.

```text
                    ┌─────────────────┐
                    │     Student     │
                    └────────┬────────┘
                             │
                     Writes code
                             │
                             ▼
                    ┌─────────────────┐
                    │   CodeAtlas IDE │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
          Code edits      Debugging       Tests
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Evidence Engine │
                    └────────┬────────┘
                             ▼
                  ┌─────────────────────┐
                  │    Student Model    │
                  └──────────┬──────────┘
                             ▼
                ┌────────────────────────┐
                │ Adaptive Learning      │
                │ Engine                 │
                └────────────┬───────────┘
                             ▼
                 ┌──────────────────────┐
                 │ Next Best Experience │
                 └──────────────────────┘
```

---

# 🔍 What Does CodeAtlas Observe?

CodeAtlas can learn from signals such as:

### Coding behavior

* Code written
* Code deleted
* Code revised
* Code structure
* Algorithm selection
* Implementation patterns
* Test creation

### Debugging behavior

* Errors encountered
* Time spent debugging
* Number of attempts
* Error progression
* Repeated failures
* Changes made after failures

### Interaction behavior

* Hints requested
* Questions asked
* Explanations requested
* Number of hints before success
* Whether the student independently solves the problem

### Problem-solving behavior

* Time to first attempt
* Time to solution
* Number of approaches
* Abandoned approaches
* Test coverage
* Solution revisions

The goal is not to collect everything.

Every signal should have a clear learning purpose.

---

# 🧩 Mistakes CodeAtlas Understands

A wrong answer is not enough information.

CodeAtlas aims to distinguish between different failure modes:

Syntax Error\
Logic Error\
Off-by-One Error\
Wrong Algorithm\
Complexity Mistake\
Requirement Misunderstanding\
Repeated Mistake\
Solution Copying\
Overengineering\


For example:

A student who repeatedly writes:

```python
for i in range(len(arr) + 1):
```

is demonstrating something different from a student who chooses:

```text
O(n²)
```

when an:

```text
O(n log n)
```

solution is required.

Both may fail.

But they require **different interventions**.

---

# 🎓 The Student Model

CodeAtlas maintains an evolving representation of the learner.

Instead of:

```text
Arrays: 80%
Graphs: 60%
DP: 40%
```

the long-term system aims for something closer to:

```text
Arrays
 ├── Traversal          → Strong
 ├── Index boundaries   → Weak
 ├── Two pointers       → Developing
 └── Complexity         → Developing

Graphs
 ├── BFS                → Strong
 ├── DFS                → Strong
 ├── Shortest path      → Developing
 └── Graph modeling     → Weak
```

But even this is not enough.

The system should eventually understand:

```text
Skill
+
Confidence
+
Evidence
+
Retention
+
Transfer
+
Recent performance
+
Mistake patterns
```

---

# 🔄 The Core Learning Loop

The heart of CodeAtlas is:

```text
Observe
   ↓
Understand
   ↓
Model
   ↓
Intervene
   ↓
Measure
   ↓
Update
   ↓
Adapt
```

More concretely:

```text
Student solves problem
        ↓
CodeAtlas observes behavior
        ↓
Detects mistakes / strategies
        ↓
Updates student model
        ↓
Estimates skill state
        ↓
Estimates retention
        ↓
Chooses next learning activity
        ↓
Student attempts again
        ↓
New evidence
        ↓
Student model improves
```

This loop is the core differentiator of the project.

---

# 🧠 Adaptive Curriculum

CodeAtlas should not simply generate:

```text
Easy
→ Medium
→ Hard
```

for everyone.

Instead:

```text
Student A
Weak in recursion
Strong in arrays
Poor retention
↓
More retrieval + recursion problems


Student B
Strong recursion
Weak graph modeling
High retention
↓
Graph modeling problems
```

The curriculum should continuously adapt to the learner.

---

# 🧑‍🏫 The Tutor

CodeAtlas should avoid immediately giving solutions.

A typical tutoring progression may be:

```text
Student stuck
     ↓
Question
     ↓
Small hint
     ↓
More targeted hint
     ↓
Conceptual explanation
     ↓
Guided reasoning
     ↓
Solution
```

The objective is:

```text
Student capability ↑
AI dependency ↓
```

The tutor should know when to stop repeatedly pushing the same question and move the learner forward.

---

# 🧠 Forgetting & Retention

Solving something once does not mean learning it permanently.

CodeAtlas therefore considers:

```text
Time since practice
+
Previous performance
+
Retrieval success
+
Mistake history
+
Difficulty
```

to estimate whether a concept should be revisited.

A student might have:

```text
Binary Search
Mastery: High
Recent practice: 2 days ago
Retention: High
```

while another concept may be:

```text
Dynamic Programming
Mastery: Medium
Last successful retrieval: 28 days ago
Retention: Uncertain
```

The second concept may deserve retrieval practice even if the student once solved it correctly.

---

# 🤖 AI Strategy

CodeAtlas is intentionally **not an LLM wrapper**.

The long-term architecture uses multiple sources of evidence:

```text
Code
+
AST
+
Compiler information
+
Runtime behavior
+
Tests
+
Code diffs
+
Interaction history
+
Statistical models
+
Student model
+
LLM reasoning
```

The LLM is one component of the intelligence layer, not the entire intelligence system.

---

# 🏗️ Architecture Philosophy

CodeAtlas will initially favor a:

> **Modular Monolith**

rather than prematurely building a distributed microservice system.

Conceptual modules include:

```text
Authentication
Problems
Coding Workspace
Code Execution
Events
Code Analysis
Mistake Detection
Skill Modeling
Behavior Modeling
Retention
Tutoring
Curriculum
Problem Generation
AI Gateway
Evaluation
```

These boundaries do not automatically mean separate services.

The architecture should evolve only when evidence justifies the complexity.

---

# 🔐 Security

CodeAtlas executes student code.

That makes security a first-class architectural concern.

The execution environment must consider:

```text
CPU limits
Memory limits
Execution timeout
Filesystem isolation
Network isolation
Process limits
Output limits
```

Student behavioral data is also treated carefully.

The system should follow:

```text
Minimum necessary data
+
Purpose-driven collection
+
Secure storage
+
Controlled access
```

---

# 📊 Evaluation

A sophisticated learning system is useless if it cannot demonstrate that students actually improve.

CodeAtlas therefore aims to evaluate:

### Immediate performance

* Problem correctness
* Error reduction
* Hint usage
* Time to solution

### Learning

* Mastery improvement
* Independent solving
* Repeated mistake reduction

### Retention

* Delayed retrieval
* Long-term performance

### Transfer

Can the student apply the concept to a different problem?

### Tutor quality

* Helpfulness
* Appropriate hint level
* Solution dependency

The key principle is:

> **Engagement is not the same thing as learning.**

---

# 🧪 Research Direction

The long-term project may explore:

Knowledge Tracing\
Bayesian Student Models\
Item Response Theory\
Contextual Bandits\
Reinforcement Learning\
Personalized Recommendation\
Spaced Retrieval\
Forgetting Models\
Code Intelligence\
Program Analysis\
Meta-Learning\
Counterfactual Learning

These should not be implemented merely because they sound advanced.

Each should be introduced when a real problem requires it and can be evaluated.

---

# 🛣️ Roadmap

The project is planned as a progression:

```text
Phase 0
Specification
   ↓
Phase 1
Engineering Foundation
   ↓
Phase 2
Coding Workspace
   ↓
Phase 3
Behavior/Event Collection
   ↓
Phase 4
Mistake Intelligence
   ↓
Phase 5
Student Modeling
   ↓
Phase 6
Adaptive Tutoring
   ↓
Phase 7
Adaptive Curriculum
   ↓
Phase 8
Retention & Forgetting
   ↓
Phase 9
Research-grade Learning Models
   ↓
Phase 10
Continuous Personalization
```

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the detailed roadmap.


AI agents must **never directly commit implementation work to `main`**.

---

# 🧑‍💻 Development Philosophy

CodeAtlas follows several principles.

### 1. Evidence over assumptions

Don't guess what the student needs.

Observe it.

### 2. Learning over engagement

A longer session is not necessarily a better session.

### 3. Simple before sophisticated

Start with understandable models.

Introduce complexity when evidence demands it.

### 4. Deterministic evidence before probabilistic interpretation

Whenever possible:

```text
Compiler
AST
Tests
Runtime
Code diff
```

should provide evidence before asking an LLM to interpret it.

### 5. Measure everything important

A claim that cannot be evaluated should be treated cautiously.

### 6. The AI should become less necessary over time

The ultimate goal is not:

> "Make the student use CodeAtlas more."

It is:

> **Make the student need CodeAtlas less.**

---

# 🧭 The North Star

A conventional coding platform asks:

> **"Did you solve the problem?"**

A coding assistant asks:

> **"How can I help you solve it?"**

CodeAtlas asks:

> **"Why are you struggling, what concept is missing, how well do you actually understand it, will you remember it later, and what should you practice next?"**

That distinction defines the project.

---

# 📜 License

CodeAtlas is licensed under the **MIT License**.

See [`LICENCE`](LICENCE).

---

# 🚧 Project Status

CodeAtlas is currently under active development.

It is not yet intended for production use.

The project is being built incrementally, with emphasis on:

```text
Correctness
+
Research quality
+
Learning effectiveness
+
Security
+
Maintainability
```

rather than rushing toward an early demo.

---

# ⭐ Long-Term Goal

The long-term goal is to build a system capable of forming a continuously improving model of one programmer:

```text
What do they know?
        ↓
What do they forget?
        ↓
Where do they struggle?
        ↓
How do they reason?
        ↓
What mistakes repeat?
        ↓
What interventions work?
        ↓
What should they learn next?
        ↓
Did they actually learn it?
```

Eventually, CodeAtlas should become something closer to a:

> **Personal learning operating system for programming.**

Not a replacement for the programmer.

A system that makes the programmer better.


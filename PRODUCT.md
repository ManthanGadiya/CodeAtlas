# CodeAtlas — Product Context

> One-line: A personal coding intelligence system that learns how you solve programming problems and teaches you what you actually need next.

## What it is

A web application where a single student solves curated Python problems in an in-browser editor. Every attempt executes in an isolated sandbox, and the system records what happened (runs, failures, hints, code evolution) as permanent evidence used to personalize learning.

## Who uses it

One student (currently the developer themself): a college programmer practicing algorithms and data structures, sitting at a desktop, in a focused study session, often late evening. The tool is quiet infrastructure for deliberate practice, not a social or marketing surface.

## Register

**Product** — design serves learning. Calm, technical, minimal, trustworthy. The interface should feel like a serious engineering tool that respects the learner's attention (docs/DESIGN.md §74). No gamification pressure, no dark patterns, no fake precision ("72% mastery" is banned; evidence-first phrasing only).

## Surfaces

1. **Dashboard** (`/`) — honest activity observations; entry point.
2. **Problem browser** (`/problems`) — curated catalog.
3. **Problem workspace** (`/problems/[slug]`) — statement + code editor + Run/Submit + results. The heart of the product.
4. **Login/bootstrap** (`/login`) — first-run account creation, then sign-in.

## Non-goals

Not a chatbot shell, not LeetCode, not engagement-optimized. AI dependency should decrease over time.

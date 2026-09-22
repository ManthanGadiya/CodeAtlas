"""Unified student state — Level 4.1 (docs/ROADMAP.md §32, docs/Data_Model.md §8).

Combines Knowledge + Mistakes + Behavior + Retention + Performance + Preferences
into a single derived projection (Data_Model §65: Student State is a projection
of Events).  Rule-based V1 — deterministic, explainable, no hidden ML — mirroring
the mastery-rule-v1 philosophy.

The unified state is computed on read from existing tables and optionally
mirrored to `student_learning_states` so that table stops being a stale
placeholder (STATUS.md M14).  Event-sourcing friendly: replay works because
the source tables are themselves projections of the immutable event stream.
"""

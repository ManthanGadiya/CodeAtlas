"""User identity module.

Owns the Student entity (docs/Data_Model.md §6). CodeAtlas initially
targets one student, but the schema stays multi-user-ready: every
user-owned resource carries a student_id so access control can tighten
later without a rewrite.
"""

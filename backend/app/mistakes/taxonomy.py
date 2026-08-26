"""Canonical mistake taxonomy reference (docs/Mistake_Taxonomy.md §5).

The full M01-M24 code list lives here as the single source used by the
migration seeder, tests, and the classifier. Descriptions stay NULL until
a detector actually exploits a category — unused documentation rots.
"""

import uuid

# (code, name) pairs, verbatim from docs/Mistake_Taxonomy.md §5.
TAXONOMY_V1 = [
    ("M01", "Syntax Error"),
    ("M02", "Compilation / Type Error"),
    ("M03", "Runtime Error"),
    ("M04", "Logic Error"),
    ("M05", "Off-by-One Error"),
    ("M06", "Wrong Algorithm"),
    ("M07", "Complexity Mistake"),
    ("M08", "Requirement Misunderstanding"),
    ("M09", "Incorrect Assumption"),
    ("M10", "Edge Case Failure"),
    ("M11", "Testing Failure"),
    ("M12", "State / Invariant Error"),
    ("M13", "Data Structure Misuse"),
    ("M14", "Recursion Error"),
    ("M15", "Concurrency / State Error"),
    ("M16", "Repeated Mistake"),
    ("M17", "Copying / Solution Dependency"),
    ("M18", "Overengineering"),
    ("M19", "Premature Optimization"),
    ("M20", "Debugging Strategy Failure"),
    ("M21", "Recognition Failure"),
    ("M22", "Transfer Failure"),
    ("M23", "Conceptual Misconception"),
    ("M24", "Forgotten Knowledge"),
]

TAXONOMY_VERSION = "taxonomy-v1"


def category_id(code: str) -> uuid.UUID:
    """Deterministic id so migration seeding and runtime stay consistent."""
    return uuid.uuid5(uuid.NAMESPACE_URL, f"codeatlas:mistake-category:{code}")

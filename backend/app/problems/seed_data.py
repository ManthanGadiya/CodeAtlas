"""Curated seed content for Phase 1.2.

Five Python problems chosen to exercise the skill graph early, with hidden
edge cases deliberately designed to surface boundary/off-by-one behaviour
(docs/Mistake_Taxonomy.md M05/M10) once analysis lands.
"""

SKILLS = [
    {"slug": "arrays", "name": "Arrays"},
    {"slug": "hash-maps", "name": "Hash Maps"},
    {"slug": "two-pointers", "name": "Two Pointers"},
    {"slug": "binary-search", "name": "Binary Search"},
    {"slug": "boundary-handling", "name": "Boundary Handling"},
    {"slug": "stacks", "name": "Stacks"},
    {"slug": "strings", "name": "Strings"},
    {"slug": "dynamic-programming", "name": "Dynamic Programming"},
]

TWO_SUM = {
    "slug": "two-sum",
    "title": "Two Sum",
    "difficulty": "easy",
    "estimated_minutes": 15,
    "function_name": "two_sum",
    "skills": [("hash-maps", "primary"), ("arrays", "supporting")],
    "description": (
        "Given an array of integers `nums` and an integer `target`, return the "
        "**indices** of the two numbers that add up to `target`.\n\n"
        "- Exactly one solution exists, and you may not use the same element twice.\n"
        "- Return them as a list `[index1, index2]`, smaller index first.\n\n"
        "Constraints:\n"
        "- `2 <= len(nums) <= 10^4`\n"
        "- Values may be negative or duplicated."
    ),
    "starter_code": (
        "def two_sum(nums: list[int], target: int) -> list[int]:\n"
        '    """Return indices of the two numbers adding up to target."""\n'
        "    pass\n"
    ),
    "test_cases": [
        {
            "name": "basic",
            "input_args": [[2, 7, 11, 15], 9],
            "expected_output": [0, 1],
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "pair-in-middle",
            "input_args": [[3, 2, 4], 6],
            "expected_output": [1, 2],
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "duplicates",
            "input_args": [[3, 3], 6],
            "expected_output": [0, 1],
            "visibility": "visible",
            "test_type": "edge",
        },
        {
            "name": "negative-values",
            "input_args": [[-3, 4, 3, 90], 0],
            "expected_output": [0, 2],
            "visibility": "hidden",
            "test_type": "edge",
        },
        {
            "name": "large-input",
            "input_args": [[i % 100 - 50 for i in range(10_000)], 97],
            "expected_output": [98, 99],
            "visibility": "hidden",
            "test_type": "normal",
        },
    ],
}

BINARY_SEARCH_FIRST_OCCURRENCE = {
    "slug": "binary-search-first-occurrence",
    "title": "Binary Search — First Occurrence",
    "difficulty": "medium",
    "estimated_minutes": 25,
    "function_name": "first_occurrence",
    "skills": [
        ("binary-search", "primary"),
        ("boundary-handling", "primary"),
        ("arrays", "supporting"),
    ],
    "description": (
        "Given a **sorted** array `nums` (may contain duplicates) and a `target`, "
        "return the index of the **first** occurrence of `target`, or `-1` if absent.\n\n"
        "- Your solution must run in O(log n).\n"
        "- The array may be empty.\n\n"
        "This problem is deliberately boundary-heavy: think carefully about what "
        "`left`, `right`, and `mid` mean at every step."
    ),
    "starter_code": (
        "def first_occurrence(nums: list[int], target: int) -> int:\n"
        '    """Return index of first occurrence of target, or -1."""\n'
        "    pass\n"
    ),
    "test_cases": [
        {
            "name": "simple-present",
            "input_args": [[1, 2, 3, 4, 5], 3],
            "expected_output": 2,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "duplicates-first-index",
            "input_args": [[1, 2, 2, 2, 3], 2],
            "expected_output": 1,
            "visibility": "visible",
            "test_type": "boundary",
        },
        {
            "name": "absent",
            "input_args": [[1, 3, 5, 7], 4],
            "expected_output": -1,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "empty-array",
            "input_args": [[], 1],
            "expected_output": -1,
            "visibility": "hidden",
            "test_type": "edge",
        },
        {
            "name": "all-duplicates",
            "input_args": [[7, 7, 7, 7], 7],
            "expected_output": 0,
            "visibility": "hidden",
            "test_type": "boundary",
        },
        {
            "name": "target-at-ends",
            "input_args": [[2, 4, 6, 8], 8],
            "expected_output": 3,
            "visibility": "hidden",
            "test_type": "boundary",
        },
    ],
}

VALID_PARENTHESES = {
    "slug": "valid-parentheses",
    "title": "Valid Parentheses",
    "difficulty": "easy",
    "estimated_minutes": 20,
    "function_name": "is_valid",
    "skills": [("stacks", "primary"), ("strings", "supporting")],
    "description": (
        "Given a string `s` containing only the characters `(`, `)`, `{`, `}`, `[`, `]`, "
        "decide whether it is **valid**: every opening bracket is closed by the same type, "
        "in the correct order.\n\n"
        "An empty string is valid."
    ),
    "starter_code": (
        "def is_valid(s: str) -> bool:\n"
        '    """Return True if the bracket string is balanced."""\n'
        "    pass\n"
    ),
    "test_cases": [
        {
            "name": "simple-pair",
            "input_args": ["()"],
            "expected_output": True,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "nested-and-mixed",
            "input_args": ["([{}])"],
            "expected_output": True,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "wrong-order",
            "input_args": ["(]"],
            "expected_output": False,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "empty-string",
            "input_args": [""],
            "expected_output": True,
            "visibility": "hidden",
            "test_type": "edge",
        },
        {
            "name": "odd-length",
            "input_args": ["(("],
            "expected_output": False,
            "visibility": "hidden",
            "test_type": "edge",
        },
        {
            "name": "closes-too-early",
            "input_args": ["]"],
            "expected_output": False,
            "visibility": "hidden",
            "test_type": "edge",
        },
    ],
}

MAX_SUBARRAY = {
    "slug": "maximum-subarray",
    "title": "Maximum Subarray",
    "difficulty": "medium",
    "estimated_minutes": 25,
    "function_name": "max_subarray_sum",
    "skills": [("dynamic-programming", "primary"), ("arrays", "supporting")],
    "description": (
        "Given an integer array `nums`, find the contiguous subarray with the "
        "**largest sum** and return that sum.\n\n"
        "- The array contains at least one number.\n"
        "- All-negative arrays are possible."
    ),
    "starter_code": (
        "def max_subarray_sum(nums: list[int]) -> int:\n"
        '    """Return the largest contiguous subarray sum."""\n'
        "    pass\n"
    ),
    "test_cases": [
        {
            "name": "classic",
            "input_args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]],
            "expected_output": 6,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "single-element",
            "input_args": [[5]],
            "expected_output": 5,
            "visibility": "visible",
            "test_type": "edge",
        },
        {
            "name": "mixed",
            "input_args": [[5, -9, 6, -2, 3]],
            "expected_output": 7,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "all-negative",
            "input_args": [[-8, -3, -6]],
            "expected_output": -3,
            "visibility": "hidden",
            "test_type": "edge",
        },
    ],
}

VALID_PALINDROME = {
    "slug": "valid-palindrome",
    "title": "Valid Palindrome",
    "difficulty": "easy",
    "estimated_minutes": 15,
    "function_name": "is_palindrome",
    "skills": [("two-pointers", "primary"), ("strings", "supporting")],
    "description": (
        "Given a string `s`, return `True` if it is a **palindrome**, considering only "
        "alphanumeric characters and ignoring case; otherwise return `False`.\n\n"
        "An empty string (or one with no alphanumeric characters) counts as a palindrome."
    ),
    "starter_code": (
        "def is_palindrome(s: str) -> bool:\n"
        '    """Return True if s is a palindrome ignoring case and non-alphanumerics."""\n'
        "    pass\n"
    ),
    "test_cases": [
        {
            "name": "sentence",
            "input_args": ["A man, a plan, a canal: Panama"],
            "expected_output": True,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "not-palindrome",
            "input_args": ["race a car"],
            "expected_output": False,
            "visibility": "visible",
            "test_type": "normal",
        },
        {
            "name": "single-char",
            "input_args": ["x"],
            "expected_output": True,
            "visibility": "visible",
            "test_type": "edge",
        },
        {
            "name": "punctuation-only",
            "input_args": [".,!?"],
            "expected_output": True,
            "visibility": "hidden",
            "test_type": "edge",
        },
        {
            "name": "numeric-string",
            "input_args": ["0P"],
            "expected_output": False,
            "visibility": "hidden",
            "test_type": "edge",
        },
    ],
}

PROBLEMS = [
    TWO_SUM,
    BINARY_SEARCH_FIRST_OCCURRENCE,
    VALID_PARENTHESES,
    MAX_SUBARRAY,
    VALID_PALINDROME,
]

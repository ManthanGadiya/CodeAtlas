"""Model registry for Alembic.

Importing this module registers every ORM model on Base.metadata so
`alembic revision --autogenerate` sees the full schema. A module that
defines models but is NOT imported here would be invisible to autogenerate
— which could make it propose destructive drops. Add one import line per
new domain-models module.
"""

import app.auth.models  # noqa: F401
import app.events.models  # noqa: F401
import app.execution.models  # noqa: F401
import app.mistakes.models  # noqa: F401
import app.problems.models  # noqa: F401
import app.skills.models  # noqa: F401
import app.users.models  # noqa: F401

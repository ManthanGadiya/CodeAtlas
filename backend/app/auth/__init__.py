"""Authentication module: password login, session cookies, account bootstrap.

Single-user by product decision (docs/PRD.md §5): registration is only
possible while no student exists. The schema itself stays multi-user-ready.
"""

from app.auth import dependencies, models, routes, schemas, security, service

__all__ = ["dependencies", "models", "routes", "schemas", "security", "service"]

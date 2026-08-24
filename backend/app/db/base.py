"""Declarative base for all CodeAtlas ORM models.

Models are introduced incrementally starting with the Version-1 core tables
defined in docs/Data_Model.md §86. Generic JSON columns are used instead of
PostgreSQL-specific types where practical so the test suite can run on
SQLite without a live PostgreSQL instance.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

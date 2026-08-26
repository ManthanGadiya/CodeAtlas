"""Learning-event recording service."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.events.models import LearningEvent

# Controlled vocabulary (subset of docs/Data_Model.md §11 used by V1).
# The stream is immutable historical truth: extend deliberately only,
# never casually (AGENTS.md §32-33).
#
# Client vs server split is an integrity boundary: the student must never
# be able to forge grading/completion evidence through POST /api/events.
CLIENT_EVENT_TYPES = {
    "PROBLEM_OPENED",
}
SERVER_EVENT_TYPES = {
    "CODE_RUN",
    "COMPILATION_FAILED",
    "RUNTIME_FAILED",
    "TEST_PASSED",
    "TEST_FAILED",
    "PROBLEM_COMPLETED",
    # Phase 2.2: deterministic mistake detection (docs/Mistake_Taxonomy.md).
    # Payload carries category_code/severity/confidence + mistake_id link.
    "MISTAKE_DETECTED",
}
EVENT_TYPES = CLIENT_EVENT_TYPES | SERVER_EVENT_TYPES

SUPPORTED_SCHEMA_VERSIONS = {1}


class UnknownEventType(ValueError):
    pass


class UnknownSchemaVersion(ValueError):
    pass


def record_event(
    db: Session,
    *,
    student_id: UUID,
    event_type: str,
    payload: dict | None = None,
    schema_version: int = 1,
) -> LearningEvent:
    if event_type not in EVENT_TYPES:
        raise UnknownEventType(event_type)
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise UnknownSchemaVersion(schema_version)

    event = LearningEvent(
        student_id=student_id,
        event_type=event_type,
        schema_version=schema_version,
        payload=payload or {},
    )
    db.add(event)
    db.commit()
    return event

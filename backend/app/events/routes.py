"""Event ingestion endpoint (client-emitted learning events)."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, DbSession
from app.events.service import (
    CLIENT_EVENT_TYPES,
    UnknownEventType,
    UnknownSchemaVersion,
    record_event,
)

router = APIRouter(prefix="/events", tags=["events"])

MAX_PAYLOAD_CHARS = 16_384


class EventIn(BaseModel):
    event_type: str = Field(max_length=48)
    payload: dict = Field(default_factory=dict)
    schema_version: int = Field(default=1, ge=1, le=99)


class EventAccepted(BaseModel):
    id: str


@router.post("", response_model=EventAccepted, status_code=status.HTTP_201_CREATED)
def ingest_event(payload: EventIn, db: DbSession, student: CurrentUser) -> EventAccepted:
    if len(str(payload.payload)) > MAX_PAYLOAD_CHARS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Event payload too large.",
        )
    # Integrity boundary: clients may only emit observational events.
    # Grading/completion evidence is recorded exclusively by the server.
    if payload.event_type not in CLIENT_EVENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unknown or server-reserved event type.",
        )
    try:
        event = record_event(
            db,
            student_id=student.id,
            event_type=payload.event_type,
            payload=payload.payload,
            schema_version=payload.schema_version,
        )
    except (UnknownEventType, UnknownSchemaVersion) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return EventAccepted(id=str(event.id))

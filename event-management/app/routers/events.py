from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import AuthenticatedUser, get_current_user, require_admin
from app.models import Registration, RegistrationStatus
from app.schemas import EventCreate, EventResponse, EventUpdate, PaginatedEvents
from app.services import (
    active_registration_count, create_event, delete_event, get_event, list_events, update_event
)

router = APIRouter(prefix="/events", tags=["Events"])


def to_event_response(db: Session, event) -> EventResponse:
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        starts_at=event.starts_at,
        location=event.location,
        capacity=event.capacity,
        active_registrations=active_registration_count(db, event.id),
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_new_event(
    data: EventCreate,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_admin),
):
    event = create_event(db, admin.organization_id, admin.id, data)
    return to_event_response(db, event)


@router.get("", response_model=PaginatedEvents)
def get_events(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    items, total = list_events(db, user.organization_id, limit, offset, search)
    return PaginatedEvents(
        items=[to_event_response(db, event) for event in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}", response_model=EventResponse)
def get_event_by_id(
    event_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    event = get_event(db, user.organization_id, event_id)
    return to_event_response(db, event)


@router.patch("/{event_id}", response_model=EventResponse)
def update_existing_event(
    event_id: UUID,
    data: EventUpdate,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_admin),
):
    if not data.model_dump(exclude_unset=True):
        raise HTTPException(status_code=422, detail="At least one field must be provided.")
    event = update_event(db, admin.organization_id, event_id, data)
    return to_event_response(db, event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_admin),
):
    delete_event(db, admin.organization_id, event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

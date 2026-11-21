from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import AuthenticatedUser, get_current_user, require_admin
from app.schemas import MyRegistrationResponse, RegistrationResponse
from app.services import cancel_registration, list_event_registrations, list_user_registrations, register_for_event

router = APIRouter(tags=["Registrations"])


@router.post(
    "/events/{event_id}/registrations",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_employee(
    event_id: UUID,
    db: Session = Depends(get_db),
    employee: AuthenticatedUser = Depends(get_current_user),
):
    """Register the authenticated employee for an event in their organization."""
    return register_for_event(db, employee.organization_id, employee.id, event_id)


@router.delete("/registrations/{registration_id}", response_model=RegistrationResponse)
def cancel_employee_registration(
    registration_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """Employees can cancel their own registration; administrators can cancel any org registration."""
    return cancel_registration(
        db, user.organization_id, user.id, user.role, registration_id
    )


@router.get(
    "/events/{event_id}/registrations",
    response_model=list[RegistrationResponse],
)
def get_registrations_for_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_admin),
):
    """List registrations for an event. Administrator access only."""
    return list_event_registrations(db, admin.organization_id, event_id)


@router.get("/registrations/mine", response_model=list[MyRegistrationResponse])
def get_my_registrations(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    rows = list_user_registrations(db, user.organization_id, user.id)
    return [
        {
            "id": registration.id,
            "event_id": registration.event_id,
            "employee_id": registration.employee_id,
            "status": registration.status,
            "created_at": registration.created_at,
            "cancelled_at": registration.cancelled_at,
            "event_title": event.title,
            "event_starts_at": event.starts_at,
            "event_location": event.location,
        }
        for registration, event in rows
    ]

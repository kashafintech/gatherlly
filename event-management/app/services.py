from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Event, Organization, Registration, RegistrationStatus, User, UserRole
)
from app.schemas import EventCreate, EventUpdate, OrganizationRegister, EmployeeCreate
from app.security import hash_password, verify_password


def register_organization(db: Session, data: OrganizationRegister) -> User:
    email = str(data.email).lower()
    org = Organization(name=data.organization_name)
    db.add(org)
    db.flush()
    user = User(
        organization_id=org.id,
        full_name=data.full_name,
        email=email,
        password_hash=hash_password(data.password),
        role=UserRole.ADMIN.value,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="An account with this email could not be created.")


def create_employee(db: Session, organization_id: UUID, data: EmployeeCreate) -> User:
    user = User(
        organization_id=organization_id,
        full_name=data.full_name,
        email=str(data.email).lower(),
        password_hash=hash_password(data.password),
        role=UserRole.EMPLOYEE.value,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="An employee with this email may already exist.")


def authenticate_user(
    db: Session,
    organization_id: UUID,
    email: str,
    password: str,
) -> User | None:
    normalized_email = email.strip().lower()

    user = db.query(User).filter(
        User.organization_id == organization_id,
        User.email == normalized_email,
        User.is_active.is_(True),
    ).first()

    if user is None or not verify_password(password, user.password_hash):
        return None

    return user


def create_event(db: Session, organization_id: UUID, creator_id: UUID, data: EventCreate) -> Event:
    event = Event(
        organization_id=organization_id,
        created_by=creator_id,
        **data.model_dump(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event(db: Session, organization_id: UUID, event_id: UUID) -> Event:
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.organization_id == organization_id,
    ).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    return event


def list_events(db: Session, organization_id: UUID, limit: int, offset: int, search: str | None):
    query = db.query(Event).filter(Event.organization_id == organization_id)
    if search:
        query = query.filter(Event.title.ilike(f"%{search}%"))
    total = query.count()
    items = query.order_by(Event.starts_at.asc()).offset(offset).limit(limit).all()
    return items, total


def active_registration_count(db: Session, event_id: UUID) -> int:
    return db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.status == RegistrationStatus.ACTIVE.value,
    ).count()


def update_event(db: Session, organization_id: UUID, event_id: UUID, data: EventUpdate) -> Event:
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.organization_id == organization_id,
    ).with_for_update().first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    changes = data.model_dump(exclude_unset=True)
    if "capacity" in changes and changes["capacity"] is not None:
        if changes["capacity"] < active_registration_count(db, event.id):
            raise HTTPException(status_code=409, detail="Capacity cannot be lower than active registrations.")
    for key, value in changes.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, organization_id: UUID, event_id: UUID) -> None:
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.organization_id == organization_id,
    ).with_for_update().first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")
    registration_exists = db.query(Registration.id).filter(Registration.event_id == event.id).first()
    if registration_exists:
        raise HTTPException(status_code=409, detail="Event has registration history and cannot be deleted.")
    db.delete(event)
    db.commit()


def register_for_event(db: Session, organization_id: UUID, employee_id: UUID, event_id: UUID) -> Registration:
    # On PostgreSQL, lock the event row so simultaneous registrations serialize
    # their capacity check. SQLite does not implement SELECT FOR UPDATE.
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.organization_id == organization_id,
    ).with_for_update().first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    existing = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.employee_id == employee_id,
    ).with_for_update().first()

    if existing and existing.status == RegistrationStatus.ACTIVE.value:
        raise HTTPException(status_code=409, detail="You are already registered for this event.")

    current_count = active_registration_count(db, event_id)
    if current_count >= event.capacity:
        raise HTTPException(status_code=409, detail="This event has reached its registration capacity.")

    if existing:
        existing.status = RegistrationStatus.ACTIVE.value
        existing.cancelled_at = None
        existing.created_at = datetime.now(timezone.utc)
        registration = existing
    else:
        registration = Registration(
            event_id=event_id,
            employee_id=employee_id,
            status=RegistrationStatus.ACTIVE.value,
        )
        db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


def cancel_registration(
    db: Session,
    organization_id: UUID,
    employee_id: UUID,
    role: str,
    registration_id: UUID,
) -> Registration:
    query = db.query(Registration).join(Event).filter(
        Registration.id == registration_id,
        Event.organization_id == organization_id,
    )
    if role != UserRole.ADMIN.value:
        query = query.filter(Registration.employee_id == employee_id)
    registration = query.with_for_update().first()
    if registration is None:
        raise HTTPException(status_code=404, detail="Registration not found.")
    if registration.status == RegistrationStatus.CANCELLED.value:
        raise HTTPException(status_code=409, detail="Registration is already cancelled.")
    registration.status = RegistrationStatus.CANCELLED.value
    registration.cancelled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(registration)
    return registration


def list_event_registrations(db: Session, organization_id: UUID, event_id: UUID):
    get_event(db, organization_id, event_id)
    return db.query(Registration).join(Event).filter(
        Registration.event_id == event_id,
        Event.organization_id == organization_id,
    ).order_by(Registration.created_at.desc()).all()


def list_user_registrations(db: Session, organization_id: UUID, employee_id: UUID):
    return (
        db.query(Registration, Event)
        .join(Event, Registration.event_id == Event.id)
        .filter(
            Event.organization_id == organization_id,
            Registration.employee_id == employee_id,
        )
        .order_by(Event.starts_at.asc())
        .all()
    )

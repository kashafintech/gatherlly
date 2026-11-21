from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import AuthenticatedUser, get_current_user, require_admin
from app.models import Organization, User
from app.schemas import (
    EmployeeCreate, LoginRequest, OrganizationRegister, ProfileResponse, TokenResponse, UserResponse
)
from app.security import create_access_token
from app.services import authenticate_user, create_employee, register_organization

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register-organization", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_organization_account(data: OrganizationRegister, db: Session = Depends(get_db)):
    """Create a new organization and its first administrator account."""
    user = register_organization(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an organization administrator or employee."""
    user = authenticate_user(
        db,
        data.organization_id,
        str(data.email),
        data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_in = create_access_token(
        user.id,
        user.organization_id,
        user.role,
    )

    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
):
    record = db.query(User).filter(User.id == user.id).first()
    organization = db.query(Organization).filter(Organization.id == user.organization_id).first()
    return {
        "id": record.id,
        "organization_id": record.organization_id,
        "full_name": record.full_name,
        "email": record.email,
        "role": record.role,
        "is_active": record.is_active,
        "organization_name": organization.name if organization else "Organization",
    }


@router.post("/employees", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def add_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    admin: AuthenticatedUser = Depends(require_admin),
):
    """Create an employee account inside the administrator's organization."""
    return create_employee(db, admin.organization_id, data)

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints
from typing import Annotated


Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
OrgName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=160)]
EventTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=160)]
Location = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=200)]
Password = Annotated[str, StringConstraints(min_length=12, max_length=128)]


class OrganizationRegister(BaseModel):
    organization_name: OrgName
    full_name: Name
    email: EmailStr
    password: Password


class EmployeeCreate(BaseModel):
    full_name: Name
    email: EmailStr
    password: Password


class LoginRequest(BaseModel):
    organization_id: UUID
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=128)]



class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    organization_id: UUID
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    title: EventTitle
    description: str | None = Field(default=None, max_length=5000)
    starts_at: datetime
    location: Location
    capacity: int = Field(gt=0, le=100000)


class EventUpdate(BaseModel):
    title: EventTitle | None = None
    description: str | None = Field(default=None, max_length=5000)
    starts_at: datetime | None = None
    location: Location | None = None
    capacity: int | None = Field(default=None, gt=0, le=100000)


class EventResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    starts_at: datetime
    location: str
    capacity: int
    active_registrations: int = 0
    model_config = ConfigDict(from_attributes=True)


class RegistrationResponse(BaseModel):
    id: UUID
    event_id: UUID
    employee_id: UUID
    status: str
    created_at: datetime
    cancelled_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginatedEvents(BaseModel):
    items: list[EventResponse]
    total: int
    limit: int
    offset: int


class ProfileResponse(UserResponse):
    organization_name: str


class MyRegistrationResponse(RegistrationResponse):
    event_title: str
    event_starts_at: datetime
    event_location: str

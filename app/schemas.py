from pydantic import (
    BaseModel,
    field_validator,
    EmailStr,
    Field,
    ConfigDict,
    FutureDatetime,
)
from datetime import datetime
from app.models import TicketStatus
from decimal import Decimal


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=14,
        description="Password length must be between 8 to 14",
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


# event schemas


class EventCreate(BaseModel):
    event_name: str = Field(
        min_length=1, description="Event name must be greater than 1 character"
    )
    date: FutureDatetime
    ticket_price: Decimal = Field(
        gt=0, description="Ticket price must be grater than 0"
    )
    total_tickets: int = Field(gt=0, description="Total tickets must be grater than 0")

    @field_validator("event_name")
    @classmethod
    def capitalize_name(cls, n):
        return n.strip().title()


class EventResponse(BaseModel):
    id: int
    event_name: str
    date: datetime
    ticket_price: Decimal
    total_tickets: int
    tickets_sold: int

    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    event_name: str | None = Field(
        default=None,
        min_length=1,
        description="Event name must be greater than 1 character",
    )
    date: FutureDatetime | None = None
    ticket_price: Decimal | None = Field(
        default=None, gt=0, description="Ticket price must be grater than 0"
    )
    total_tickets: int | None = Field(
        default=None, gt=0, description="Total tickets must be grater than 0"
    )

    @field_validator("event_name")
    @classmethod
    def capitalize_name(cls, n):
        if n is None:
            return n
        return n.strip().title()


# ticket schema


class TicketCreate(BaseModel):
    event_id: int = Field(gt=0, description="Event id must be greater than 0")


class TicketResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    status: TicketStatus
    purchase_date: datetime

    event: EventResponse

    model_config = ConfigDict(from_attributes=True)

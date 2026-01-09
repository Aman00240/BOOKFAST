import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Enum as SAEnum
from datetime import datetime
from decimal import Decimal
from app.database import Base


class TicketStatus(str, enum.Enum):
    booked = "booked"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    tickets = relationship("Ticket", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_name: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ticket_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    total_tickets: Mapped[int] = mapped_column(Integer)
    tickets_sold: Mapped[int] = mapped_column(Integer, default=0)

    tickets = relationship(
        "Ticket", back_populates="event", cascade="all, delete-orphan"
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    purchase_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    status: Mapped[TicketStatus] = mapped_column(
        SAEnum(TicketStatus), default=TicketStatus.booked
    )

    owner = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")

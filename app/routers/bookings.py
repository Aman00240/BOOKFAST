from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user


router = APIRouter(tags=["Bookings"])


@router.post("/book", response_model=schemas.TicketResponse)
async def book_ticket(
    ticket_data: schemas.TicketCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    query = (
        select(models.Event)
        .where(models.Event.id == ticket_data.event_id)
        .with_for_update()
    )

    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.tickets_sold >= event.total_tickets:
        raise HTTPException(status_code=400, detail="Sold Out")

    event.tickets_sold += 1

    new_ticket = models.Ticket(event_id=event.id, user_id=current_user.id)

    db.add(new_ticket)

    await db.commit()
    await db.refresh(new_ticket)

    new_ticket.event = event

    return new_ticket


@router.post("/tickets/{ticket_id}/cancel", response_model=schemas.TicketResponse)
async def cancel_ticket(
    ticket_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    query = (
        select(models.Ticket)
        .join(models.Ticket.event)
        .options(contains_eager(models.Ticket.event))
        .where(models.Ticket.id == ticket_id)
        .with_for_update()
    )

    result = await db.execute(query)
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to cancel this ticket"
        )

    if ticket.status == models.TicketStatus.cancelled:
        raise HTTPException(status_code=400, detail="Ticket is already cancelled")

    ticket.status = models.TicketStatus.cancelled
    ticket.event.tickets_sold -= 1

    await db.commit()

    return ticket

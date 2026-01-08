from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(tags=["Events"])


@router.post("/events", response_model=schemas.EventResponse)
async def create_event(
    event: schemas.EventCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    new_event = models.Event(
        event_name=event.event_name,
        date=event.date,
        ticket_price=event.ticket_price,
        total_tickets=event.total_tickets,
    )

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return new_event


@router.get("/events", response_model=list[schemas.EventResponse])
async def get_events(
    db: Annotated[AsyncSession, Depends(get_db)], skip: int = 0, limit: int = 10
):
    query = select(models.Event).offset(skip).limit(limit)

    result = await db.execute(query)
    events = result.scalars().all()

    return events


@router.get("/event/{event_id}", response_model=schemas.EventResponse)
async def get_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    event = await db.get(models.Event, event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event Not Found")

    return event


@router.patch("/events/{event_id}", response_model=schemas.EventResponse)
async def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    event = await db.get(models.Event, event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event Not Found")

    update_data = event_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event, key, value)

    if "total_tickets" in update_data:
        if event.total_tickets < event.tickets_sold:
            raise HTTPException(
                status_code=400, detail="Cannot reduce capacity below sold tickets"
            )

    await db.commit()
    await db.refresh(event)
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    event = await db.get(models.Event, event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.tickets_sold > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete event with active ticket sales. Cancel tickets first.",
        )

    await db.delete(event)
    await db.commit()

    return None

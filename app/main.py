from fastapi import FastAPI
from app.routers import users, events, bookings

app = FastAPI()

app.include_router(users.router)
app.include_router(events.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return {"message": "BookFast API"}

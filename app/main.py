from fastapi import FastAPI
from app.routers import users

app = FastAPI()

app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "BookFast API"}

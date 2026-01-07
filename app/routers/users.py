from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app import models, schemas, auth
from app.database import get_db


router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user_data: schemas.UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    # --- ADD THESE 3 LINES ---
    print(f"DEBUG: Type of password is: {type(user_data.password)}")
    print(f"DEBUG: Value of password is: {user_data.password}")
    print(f"DEBUG: Length is: {len(str(user_data.password))}")
    # -------------------------
    existing_user = await db.scalar(
        select(models.User).where(models.User.email == user_data.email)
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Email Already Registered")

    hashed_pwd = auth.get_password_hash(user_data.password)

    new_user = models.User(email=user_data.email, password=hashed_pwd)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.scalar(
        select(models.User).where(models.User.email == form_data.username)
    )

    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Email or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

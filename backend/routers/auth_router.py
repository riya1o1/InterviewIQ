from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=schemas.TokenResponse)
def signup(data: schemas.SignupRequest, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = models.User(
        name=data.name,
        email=data.email,
        password=auth.hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return token immediately — no need to login again
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token}


@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user or not auth.verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token}


@router.get("/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

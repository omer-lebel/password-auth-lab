from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select
from models import User, UserCredentials
from database import get_session
from server.hashing import HashProvider

router = APIRouter(tags=["auth"])

def get_hash_provider_dependency(request: Request):
    return request.app.state.hash_provider

@router.post("/register")
def register(
        user: UserCredentials,
        session: Session = Depends(get_session),
        hasher: HashProvider = Depends(get_hash_provider_dependency)):

    # Check if user exists
    query = select(User).where(User.username == user.username)
    if session.exec(query).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hashed_pwd = hasher.hash_password(user.password)
    db_user = User(username=user.username, password=hashed_pwd)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": f"Register successful, welcome {db_user.username}" }



@router.post("/login")
def login(
        user: UserCredentials,
        session: Session = Depends(get_session),
        hasher: HashProvider = Depends(get_hash_provider_dependency)):

    # Find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # record attempt

    # Verify password
    if hasher.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": f"Login successful, welcome back {db_user.username}"}
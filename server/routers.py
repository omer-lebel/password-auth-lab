from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from models import User, UserCredentials
from database import get_session

router = APIRouter(tags=["auth"])


@router.post("/register")
def register(user: UserCredentials, session: Session = Depends(get_session)):
    # Check if user exists
    query = select(User).where(User.username == user.username)
    if session.exec(query).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    db_user = User(username=user.username, password=user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": f"Register successful, welcome {db_user.username}" }



@router.post("/login")
def login(user: UserCredentials, session: Session = Depends(get_session)):
    # Find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # record attempt

    # Verify password
    if user.password != db_user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": f"Login successful, welcome back {db_user.username}"}
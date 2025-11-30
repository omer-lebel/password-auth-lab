from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select

from server.models import UserCredentials
from server.database import get_session, User
from server.hashing import HashProvider

router = APIRouter(tags=["auth"])

def get_hash_provider_dependency(request: Request):
    return request.app.state.hash_provider

def get_logger_dependency(request: Request):
    return request.app.state.logger

@router.post("/register")
def register(
        user: UserCredentials,
        session: Session = Depends(get_session),
        log = Depends(get_logger_dependency),
        hasher: HashProvider = Depends(get_hash_provider_dependency),
        request: Request = None):

    client_ip = request.client.host
    log.debug(f"{client_ip} request register with username {user.username}")

    # Check if user exists
    query = select(User).where(User.username == user.username)
    if session.exec(query).first():
        log.debug(f"{client_ip} registration failed - username '{user.username}' taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hashed_pwd = hasher.hash_password(user.password)
    db_user = User(username=user.username, password=hashed_pwd)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    log.debug(f"{client_ip} registration success")
    return {"message": f"Register successful, welcome {user.username}" }



@router.post("/login")
def login(
        user: UserCredentials,
        session: Session = Depends(get_session),
        log = Depends(get_logger_dependency),
        hasher: HashProvider = Depends(get_hash_provider_dependency),
        request: Request = None):

    client_ip = request.client.host
    log.debug(f"{client_ip} request login with username {user.username}")

    # Find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()
    if not db_user:
        log.audit(ip=client_ip, username=user.username, attempt_count=-1, success=False, reason="User not found")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not hasher.verify_password(user.password, db_user.password):
        log.audit(ip=client_ip, username=user.username, attempt_count=-1, success=False, reason="Wrong password")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    log.audit(ip=client_ip, username=user.username, attempt_count=-1, success=True, reason="success")
    return {"message": f"Login successful, welcome back {db_user.username}"}
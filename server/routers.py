from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select

from server.log import get_logger
from server.schema import UserRegister, UserLogin
from server.database import get_session, User
from server.hashing import HashProvider
from server.protection import ProtectionManager, ProtectionResult


router = APIRouter(tags=["auth"])
log = get_logger()

@router.post("/register")
async def register(
        user: UserRegister,
        session: Session = Depends(get_session),
        request: Request = None):

    client_ip = request.client.host
    log.debug(f"{client_ip} request register with username {user.username}")

    # Check if user exists
    query = select(User).where(User.username == user.username)
    if session.exec(query).first():
        log.debug(f"{client_ip} registration failed - username '{user.username}' taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create new user
    hasher: HashProvider = request.app.state.hash_provider
    hashed_pwd = hasher.hash_password(user.password)
    db_user = User(username=user.username, password=hashed_pwd, totp_secret=user.totp_secret)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    log.debug(f"{client_ip} registration success")
    return {"message": f"Register successful, welcome {user.username}" }


@router.post("/login")
async def login(
        user: UserLogin,
        session: Session = Depends(get_session),
        request: Request = None):

    client_ip = request.client.host
    log.debug(f"{client_ip} request login with username {user.username}")
    protections: ProtectionManager = request.app.state.protection_mng

    # Find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()
    request.state.username = user.username
    if not db_user:
        request.state.failure_reason = "Unknown username"
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # check if user currently block
    result: ProtectionResult = protections.validate_request(user=db_user, captcha_token=user.captcha_token, totp_code=user.totp_code)
    if not result.allowed:
        request.state.failure_reason = result.reason
        raise HTTPException(status_code=result.status_code, detail=result.user_msg)

    # Verify password
    hasher: HashProvider = request.app.state.hash_provider
    if not hasher.verify_password(user.password, db_user.password):
        protections.record_failure(db_user)
        session.commit()
        request.state.failure_reason = "Wrong password"
        raise HTTPException(status_code=401, detail="Wrong username or password")

    # verify totp if needed
    if not protections.verify_totp(db_user.totp_secret, user.totp_code):
        protections.record_failure(db_user)
        session.commit()
        request.state.failure_reason = "Invalid TOTP"
        raise HTTPException(status_code=401, detail="Invalid TOTP code")


    protections.reset(db_user)
    session.commit()
    return {"message": f"Login successful, welcome back {db_user.username}"}


@router.post("/admin/generate_token/{group_seed}")
async def generate_captcha_token(
        input_group_seed: int,
        username: str,
        session: Session = Depends(get_session),
        request: Request = None):

    protections: ProtectionManager = request.app.state.protection_mng

    # verify user and make sure it has the right group seed
    query = select(User).where(User.username == username)
    exist_user = session.exec(query).first()
    if not exist_user or protections.group_seed != input_group_seed:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    token = protections.generate_captcha_token(username)
    return {"captcha_token": token}
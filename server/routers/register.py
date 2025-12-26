from fastapi import APIRouter, HTTPException, Depends, Request
from http import HTTPStatus
from sqlmodel import Session, select
from zxcvbn import zxcvbn

from server.log import get_logger
from server.schema import UserRegister
from server.database import db_manager, User
from server.hashing import HashProvider
from server.protection import ProtectionManager


register_router = APIRouter(tags=["register"])
log = get_logger()

@register_router.post("/register")
def register(
        user: UserRegister,
        session: Session = Depends(db_manager.get_session),
        request: Request = None):

    log.info(f"{user.username:<10} | request register")

    # check if user exists
    query = select(User).where(User.username == user.username)
    if session.exec(query).first():
        log.info(f"{user.username:<10} | failed - username '{user.username}' taken")
        raise HTTPException(status_code=400, detail="Username already exist")

    # verify totp secret if needed
    protections: ProtectionManager = request.app.state.protection_mng
    totp_enable = (protections.totp and user.totp_secret) is not None
    if totp_enable and not protections.totp.is_valid_secret(user.totp_secret):
            raise HTTPException(status_code=400, detail="Invalid totp (use pyotp.random_base32() to generate totp secret)")

    # create new user
    hasher: HashProvider = request.app.state.hash_provider
    hashed_pwd = hasher.hash_password(user.password)
    password_score = classify_password_strength(user.password)
    db_user = User(username=user.username, password=hashed_pwd, password_score=password_score, totp_secret=user.totp_secret)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    log.info(f"{user.username:<10} | SUCCESS - password: [{password_score}], totp: [{totp_enable}]")
    return {"message": f"Register successful, welcome {user.username}" }


def classify_password_strength(plain_password: str):
    score = zxcvbn(plain_password)['score']
    if score <= 1:
        return "weak"
    elif score == 2:
        return "medium"
    else:
        return "strong"
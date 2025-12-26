from fastapi import APIRouter, HTTPException, Depends, Request
from http import HTTPStatus
from sqlmodel import Session, select

from server.log import get_logger
from server.schema import UserRegister, UserLogin
from server.database import db_manager, User
from server.hashing import HashProvider
from server.protection import ProtectionManager, ProtectionResult


login_router = APIRouter(tags=["login"])
log = get_logger()

@login_router.post("/login")
async def login(
        user: UserLogin,
        session: Session = Depends(db_manager.get_session),
        request: Request = None):

    log.info(f"{user.username:<10} | request")
    protections: ProtectionManager = request.app.state.protection_mng

    # find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()
    request.state.username = user.username
    if not db_user:
        request.state.failure_reason = "Unknown username"
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Wrong username or password")

    request.state.password_score = db_user.password_score

    # check if user currently block
    result: ProtectionResult = protections.validate_request(user=db_user, captcha_token=user.captcha_token)
    if not result.allowed:
        request.state.failure_reason = result.reason
        raise HTTPException(status_code=result.status_code, detail=result.user_msg)

    # verify password
    hasher: HashProvider = request.app.state.hash_provider
    if not hasher.verify_password(user.password, db_user.password):
        protections.record_failure(db_user)
        session.commit()
        request.state.failure_reason = "Wrong password"
        # captcha
        if protections.totp and db_user.user.captcha_required:
            raise HTTPException(status_code=HTTPStatus.PRECONDITION_REQUIRED, detail="required captcha")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Wrong username or password")

    # totp
    if protections.totp and db_user.totp_secret:
        protections.totp.init_pending_session(db_user)
        request.state.failure_reason = "totp"
        session.commit()
        raise HTTPException(status_code=HTTPStatus.ACCEPTED, detail="Password verified, required TOTP. Please call /login_totp")

    protections.reset(db_user)
    session.commit()
    log.info(f"{user.username:<10} | SUCCESS")
    return {"message": f"Login successful, welcome back {db_user.username}"}
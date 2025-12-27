from fastapi import APIRouter, HTTPException, Depends, Request
from http import HTTPStatus
from sqlmodel import Session, select

from server.log import get_logger
from server.protection.base import AuthContext
from server.schema import TotpLogin
from server.database import db_manager, User
from server.protection import ProtectionManager, ProtectionResult


login_totp_router = APIRouter(tags=["login"])
log = get_logger()

@login_totp_router.post("/login_totp")
def login_totp(
        user: TotpLogin,
        session: Session = Depends(db_manager.get_session),
        request: Request = None):

    log.info(f"{user.username:<10}| request login_totp")
    protections: ProtectionManager = request.app.state.protection_mng

    if not protections.totp:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Not found")

    # find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()
    if not db_user:
        log.debug(f"{user.username:<10} | FAILED -  unknown username")
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid username or totp code")

    # verify totp session not expired
    result: ProtectionResult = protections.totp.validate_request(AuthContext(user=db_user))
    if not result.allowed:
        session.commit()
        raise HTTPException(status_code=result.status_code, detail=result.user_msg)

    # verify totp code
    if not protections.totp.verify_code(username=db_user.username, totp_secret=db_user.totp_secret, input_code=user.totp_code):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Invalid TOTP code")

    protections.totp.reset(db_user)
    session.commit()
    log.info(f"{user.username:<10} | SUCCESS")
    return {"message": f"Login successful, welcome back {db_user.username}"}
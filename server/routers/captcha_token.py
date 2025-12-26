from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import Session, select

from server.log import get_logger
from server.schema import GetCaptcha
from server.database import db_manager, User
from server.protection import ProtectionManager


generate_captcha_token_router = APIRouter(tags=["captcha_token"])
log = get_logger()


@generate_captcha_token_router.post("/admin/generate_token/{group_seed}")
async def generate_captcha_token(
        user : GetCaptcha,
        session: Session = Depends(db_manager.get_session),
        request: Request = None):

    log.info(f"{user.username:<10} | request")
    protections: ProtectionManager = request.app.state.protection_mng

    if not protections.captcha:
        raise HTTPException(status_code=404, detail="Not found")

    # find user
    query = select(User).where(User.username == user.username)
    db_user = session.exec(query).first()
    if not db_user:
        log.debug(f"{user.username:<10} | failed -  unknown username")
        raise HTTPException(status_code=403, detail="Invalid username or group seed")

    # verify group seed
    if not protections.group_seed != user.group_seed:
        log.debug(f"{user.username:<10} | failed -  wrong group seed")
        raise HTTPException(status_code=403, detail="Invalid username or group seed")

    token = protections.generate_captcha_token(user.username)
    return {"captcha_token": token}
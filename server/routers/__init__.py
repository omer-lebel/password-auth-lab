from server.routers.login import login_router
from server.routers.login_totp import login_totp_router
from server.routers.register import register_router
from server.routers.captcha_token import generate_captcha_token_router

__all__ = [
    "login_router",
    "login_totp_router",
    "register_router",
    "generate_captcha_token_router"
]
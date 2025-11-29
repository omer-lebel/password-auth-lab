import argparse

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from routers import router
import uvicorn

from config.config import AppConfig
from database import create_db_and_tables
from hashing import get_hash_provider
from server.config import HashingConfig

PORT = 8080

def parse_args():
    parser = argparse.ArgumentParser(description="Auth API Server")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to config JSON file (default: config.json)"
    )
    return parser.parse_args()


def configure_app(app: FastAPI, hash_conf: HashingConfig) -> None:
    create_db_and_tables()
    app.state.hash_provider = get_hash_provider(hash_conf)
    app.include_router(router)

    @app.get("/")
    def read_root():
        return RedirectResponse(url="/docs")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"detail": "Invalid input data"}
        )


def main():
    args = parse_args()
    app_config = AppConfig.from_json(args.config)

    app = FastAPI(title="Auth API")
    configure_app(app, app_config.hashing)
    uvicorn.run(app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()



# python sever.py --hash=sha256 --salt=true --peper="to" --rateLimit=t
"""
 palin text?
 salt - uniq prefix to password
 pepper - same prefix to password, env var. what is the point, attack are online!
 rate limit (per user) - ?
 account lockout - ?
 captcha - token the user get after 10 attempts
 TOTP - auth base time + shared secret. should we add more endpoint for register with totp?
 
 Ihash: abstract verify()
    --- sha256
    --- argon2
    --- dammyHash 
"""
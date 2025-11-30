import argparse
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers import router
import uvicorn

from config.config import AppConfig
from database import create_db_and_tables
from hashing import get_hash_provider
from log import setup_logger, get_logger
from server.config import HashingConfig

PORT = 8080

"""
todo:
1. logger - first priority
2. attempt.json 
3. protection - pepper, ask in the forum about the other
4. rate limiting (sec / min / hour / user??)
5. 
"""

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
    app.state.logger = get_logger()
    app.include_router(router)

    @app.get("/")
    def read_root():
        return RedirectResponse(url="/docs")


def main():
    args = parse_args()
    app_config = AppConfig.from_json(args.config)
    log = setup_logger(app_config.logging.path)

    app = FastAPI(title="Auth API")

    configure_app(app, app_config.hashing)

    log.info(f"started server on http://127.0.0.1:{PORT} (Press CTRL+C to quit)")
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
"""
import argparse
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from server.protection.protection_manager import ProtectionManager
from server.middlewares import AuditMiddleware
from server.routers import router
from server.config.config import AppConfig
from server.database import create_db_and_tables
from server.hashing import HashProviderFactory
from server.log import AuditConfig, setup_logger

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


def configure_app(app: FastAPI, conf: AppConfig) -> None:
    create_db_and_tables()
    app.state.hash_provider = HashProviderFactory(conf=conf.hashing, pepper=conf.PEPPER).create()
    app.state.protection_mng = ProtectionManager(conf=conf.protection, group_seed=conf.group_seed)
    app.add_middleware(AuditMiddleware)
    app.include_router(router)

    @app.get("/")
    def read_root():
        return RedirectResponse(url="/docs")


def main():

    args = parse_args()
    conf = AppConfig.from_json(args.config)

    audit_config = AuditConfig(
        hash_type=conf.hashing.type,
        pepper_enable=conf.hashing.pepper_enable,
        account_lockout_enable=conf.protection.account_lockout.enabled,
        rate_limit_enable=conf.protection.rate_limiting.enabled)

    log = setup_logger(audit_config, conf.logging.path)
    log.debug(f"configure server with: {conf}")

    app = FastAPI(title="Auth API")

    configure_app(app, conf)

    log.info(f"started server on http://127.0.0.1:{PORT} (Press CTRL+C to quit)")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info", access_log=False)


if __name__ == "__main__":
    main()
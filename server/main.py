import argparse
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pathlib import Path
import shutil
import uvicorn

from server.protection import ProtectionManager
from server.middlewares import AuditMiddleware
from server.routers import router
from server.config import AppConfig
from server.database import db_manager
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
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for database, logs, and config copy"
    )
    return parser.parse_args()


def setup_output_directory(output_dir: str) -> Path:
    if not output_dir:
        return Path.cwd()

    path = Path(output_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_config_file_to_output_dir(config_src: str, output_dir: Path, log):
    try:
        src_path = Path(config_src).resolve()
        dest_path = output_dir / src_path.name

        if src_path == dest_path:
            log.debug("Config source and output destination are the same, skipping copy.")
            return

        shutil.copy2(src_path, dest_path)
    except Exception as e:
        log.error(f"Failed to copy config file: {e}")


def configure_app(app: FastAPI, conf: AppConfig) -> None:
    app.state.hash_provider = HashProviderFactory(conf=conf.hashing, pepper=conf.PEPPER).create()
    app.state.protection_mng = ProtectionManager(conf=conf.protection, group_seed=conf.group_seed)
    app.add_middleware(AuditMiddleware)
    app.include_router(router)

    @app.get("/")
    def read_root():
        return RedirectResponse(url="/docs")


def main():
    args = parse_args()
    output_dir = setup_output_directory(args.output)
    conf = AppConfig.from_json(args.config)

    audit_config = AuditConfig(
        hash_type=conf.hashing.type,
        pepper_enable=conf.hashing.pepper_enable,
        account_lockout_enable=conf.protection.account_lockout.enabled,
        rate_limit_enable=conf.protection.rate_limiting.enabled,
        captcha_enable=conf.protection.captcha.enabled,
        totp_enable=conf.protection.totp.enabled)

    log = setup_logger(audit_config, conf.log_level, output_dir)
    log.debug(f"configure server with: {conf}")
    copy_config_file_to_output_dir(config_src=args.config, output_dir=output_dir, log=log)
    log.info(f"output directory for log db and conf file: {output_dir}")

    db_manager.initialize(output_dir)
    app = FastAPI(title="Auth API")
    configure_app(app, conf)

    log.info(f"started server on http://127.0.0.1:{PORT} (Press CTRL+C to quit)")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info", access_log=False)


if __name__ == "__main__":
    main()

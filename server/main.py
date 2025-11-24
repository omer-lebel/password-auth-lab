import argparse
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
from routers import router
from database import create_db_and_tables

"""We will parse the args with this latter"""
# def parse_args():
#     parser = argparse.ArgumentParser(description="Auth API Server")
#     parser.add_argument(
#         "--hash",
#         type=str,
#         choices=["bcrypt", "bcrypt", "argon2", "debug"],
#         help="Password hashing algorithm to use"
#     )
#     return parser.parse_args()
#
# def get_hash_provider(hash_type: str) -> HashProvider:
#     providers = {
#         "bcrypt": BcryptHashProvider(),
#         "sha256": SHA256HashProvider(),
#         "argon2": Argon2HashProvider(),
#         "debug": NoHashProvider()
#     }
#     if not hash_type in providers:
#         raise Exception(f"Hash type {hash_type} not supported")
#     return providers[hash_type]



def configure_app(app: FastAPI):
    create_db_and_tables()
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
    app = FastAPI(title="Auth API", version="1.0.0")
    configure_app(app)
    uvicorn.run(app, host="127.0.0.1", port=8000)


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
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from .api import router
from .deps import db

app = FastAPI(
    title="Wallet API",
    version="1.0",
)
app.include_router(router)


@app.on_event("startup")
async def startup():
    await db._db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db._db.disconnect()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"errors": exc.errors()}),
    )

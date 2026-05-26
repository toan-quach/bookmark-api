from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import auth, bookmarks, tags, users
from app.schemas.schemas import ErrorDetail, ErrorResponse

app = FastAPI(
    title="Bookmarks API",
    version="1.0.0",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Not found"},
        409: {"model": ErrorResponse, "description": "Conflict"},
    },
)


app.include_router(users.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err["loc"] if loc != "body")
        details.append(ErrorDetail(field=field or None, message=err["msg"]))
    body = ErrorResponse(error="Validation error", details=details)
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    body = ErrorResponse(error=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    body = ErrorResponse(error="Internal server error")
    return JSONResponse(status_code=500, content=body.model_dump())


@app.get("/health")
def health():
    return {"status": "ok"}

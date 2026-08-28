import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware

configure_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", description="Evidence-based research project collaboration APIs for M.Tech students.")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RequestLoggingMiddleware)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health", tags=["System"])
def health_check(): return {"status": "healthy", "environment": settings.environment}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Validation failed", "errors": exc.errors()})


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(_: Request, exc: SQLAlchemyError):
    logging.getLogger(__name__).exception("Database error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "A database error occurred"})

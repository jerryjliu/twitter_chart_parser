"""FastAPI backend for Twitter chart parser."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.extract import router as extract_router
from api.parse import router as parse_router
from api.validate import router as validate_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("twitter_chart_parser")


app = FastAPI(
    title="Twitter Chart Parser API",
    version="1.0.0",
    description="Extract tweet images and parse chart/table content into markdown.",
)


def _build_error_payload(
    *,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create standard API error payload."""
    payload: dict[str, Any] = {
        "error_code": error_code,
        "message": message,
    }
    if details:
        payload["details"] = details
    return payload


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log request context and latency for every request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """Return HTTP errors in consistent format."""
    detail = exc.detail
    if isinstance(detail, dict) and "error_code" in detail and "message" in detail:
        payload = detail
    elif isinstance(detail, str):
        payload = _build_error_payload(error_code="HTTP_ERROR", message=detail)
    else:
        payload = _build_error_payload(error_code="HTTP_ERROR", message="Request failed", details={"detail": detail})

    return JSONResponse(status_code=exc.status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Return input validation errors in consistent format."""
    return JSONResponse(
        status_code=422,
        content=_build_error_payload(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": exc.errors()},
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return fallback error envelope for uncaught errors."""
    logger.exception("unhandled_error", extra={"error": str(exc)})
    return JSONResponse(
        status_code=500,
        content=_build_error_payload(error_code="INTERNAL_ERROR", message="Unexpected server error"),
    )


cors_origins_env = os.environ.get("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(validate_router)
app.include_router(extract_router)
app.include_router(parse_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health endpoint for uptime checks."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

"""
Main entry point for the Multi-Agent Code Pipeline FastAPI application.
Configures middleware, exception handlers, and application lifecycle.
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers.router import router
from models.api_response_dto import APIResponse, Error
from utils.exceptions.custom_app_exception import CustomAppException
from utils.exceptions.error_codes import ErrorCode
from utils.exceptions.http_status import HttpStatusCode
from migration.migration import migration


async def lifespan(app: FastAPI):
    """Runs database migration on startup before accepting requests."""
    migration.run_startup_migration()
    yield


app = FastAPI(
    title="Multi-Agent Code Pipeline API",
    description="An intelligent pipeline that codes, reviews, and researches using LLM agents.",
    version="1.0.0",
    lifespan=lifespan
)

# ── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST","GET"],
    allow_headers=["*"]
)

app.include_router(router)

# ── Exception Handlers ─────────────────────────────────────────────────────────

@app.exception_handler(CustomAppException)
async def custom_app_exception_handler(request: Request, exc: CustomAppException)-> JSONResponse:
    """Handles all CustomAppExceptions and returns a standardized JSON error response."""
    api_response = exc.to_api_response()
    return JSONResponse(
        status_code=exc.status_code,
        content=api_response.to_dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError)-> JSONResponse:
    """Handles Pydantic request validation errors and returns structured field-level messages."""
    errors = [
        Error(
            code=ErrorCode.VALIDATION_ERROR,
            message=f"{error['loc'][-1]}: {error['msg']}"
        )
        for error in exc.errors()
    ]
    api_response = APIResponse(
        data=None,
        errors=errors,
        code=HttpStatusCode.UNPROCESSABLE_ENTITY
    )
    return JSONResponse(
        status_code=HttpStatusCode.UNPROCESSABLE_ENTITY,
        content=api_response.to_dict()
    )


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """Runs the FastAPI application locally using Uvicorn."""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )

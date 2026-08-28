from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from customer_service_agent.api.health import router as health_router
from customer_service_agent.api.routes.conversations import (
    router as conversations_router,
)
from customer_service_agent.api.routes.messages import router as messages_router
from customer_service_agent.core.config import get_settings
from customer_service_agent.core.exceptions import AppError, NotFoundError
from customer_service_agent.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(conversations_router)
    app.include_router(messages_router)

    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(AppError, app_error_handler)
    app.middleware("http")(log_requests)

    return app


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("application_error error=%s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


async def log_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[JSONResponse]],
) -> JSONResponse:
    logger.info("request_start method=%s path=%s", request.method, request.url.path)
    response = await call_next(request)
    logger.info(
        "request_end method=%s path=%s status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


app = create_app()

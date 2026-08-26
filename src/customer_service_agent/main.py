from fastapi import FastAPI

from customer_service_agent.api.health import router as health_router
from customer_service_agent.api.routes.conversations import (
    router as conversations_router,
)
from customer_service_agent.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(conversations_router)
    return app


app = create_app()

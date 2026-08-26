from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from customer_service_agent.core.config import get_settings


def create_engine() -> AsyncEngine:
    """Create the application's asynchronous database engine."""
    return create_async_engine(
        get_settings().database_url,
        echo=False,
        pool_pre_ping=True,
    )


engine = create_engine()
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Yield one database session and close it after the request finishes."""
    async with SessionFactory() as session:
        yield session

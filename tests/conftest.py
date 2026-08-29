from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from customer_service_agent.main import app


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """A TestClient sharing one event loop for the whole session.

    The SQLAlchemy async engine is created at module import time, so its
    connection pool is bound to one event loop. ``with TestClient(app)``
    starts a single portal/event loop that all requests share; without it,
    every request would run on a fresh loop and break pooled connections.
    """
    with TestClient(app) as test_client:
        yield test_client

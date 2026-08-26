from fastapi.testclient import TestClient

from customer_service_agent.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "customer-service-agent",
    }


def test_get_missing_conversation_returns_404() -> None:
    response = client.get("/api/conversations/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}

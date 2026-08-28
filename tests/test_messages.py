from uuid import uuid4

from fastapi.testclient import TestClient


def _create_conversation(client: TestClient) -> dict[str, str]:
    response = client.post("/api/conversations", json={"title": "Test chat"})
    assert response.status_code == 201
    return dict(response.json())


def test_create_message_in_missing_conversation_returns_404(client: TestClient) -> None:
    response = client.post(
        f"/api/conversations/{uuid4()}/messages",
        json={"role": "user", "content": "Hello"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Conversation not found"}


def test_create_and_list_messages(client: TestClient) -> None:
    conversation = _create_conversation(client)
    conversation_id = conversation["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "How do I create a discount?"},
    )

    assert response.status_code == 201
    message = response.json()
    assert message["conversation_id"] == conversation_id
    assert message["role"] == "user"
    assert message["content"] == "How do I create a discount?"

    response = client.get(f"/api/conversations/{conversation_id}/messages")

    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["id"] == message["id"]

    client.delete(f"/api/conversations/{conversation_id}")


def test_delete_conversation_removes_its_messages(client: TestClient) -> None:
    conversation = _create_conversation(client)
    conversation_id = conversation["id"]

    client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "Hello"},
    )

    response = client.delete(f"/api/conversations/{conversation_id}")

    assert response.status_code == 204

    response = client.get(f"/api/conversations/{conversation_id}/messages")
    assert response.status_code == 404


def test_create_message_with_invalid_role_returns_422(client: TestClient) -> None:
    conversation = _create_conversation(client)
    conversation_id = conversation["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "robot", "content": "Hello"},
    )

    assert response.status_code == 422

    client.delete(f"/api/conversations/{conversation_id}")

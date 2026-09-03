import asyncio
from types import SimpleNamespace

from customer_service_agent.knowledge.embeddings import EmbeddingService


class FakeEmbeddings:
    """Gia lap API embeddings: tra vector gia, khong goi mang."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, list[str]]] = []

    async def create(self, model: str, input: list[str]) -> SimpleNamespace:
        self.calls.append((model, input))
        return SimpleNamespace(data=[SimpleNamespace(embedding=[0.1] * 1536) for _ in input])


class FakeClient:
    """Gia lap AsyncOpenAI: chi co thuoc tinh embeddings."""

    def __init__(self) -> None:
        self.embeddings = FakeEmbeddings()


def test_embed_returns_one_vector_per_text() -> None:
    fake = FakeClient()
    service = EmbeddingService(client=fake)  # type: ignore[arg-type]
    vectors = asyncio.run(service.embed(["hello", "world"]))

    assert len(vectors) == 2
    assert len(vectors[0]) == 1536


def test_embed_empty_list_does_not_call_api() -> None:
    fake = FakeClient()
    service = EmbeddingService(client=fake)  # type: ignore[arg-type]
    vectors = asyncio.run(service.embed([]))

    assert vectors == []
    assert fake.embeddings.calls == []

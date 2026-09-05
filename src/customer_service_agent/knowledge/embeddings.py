from openai import AsyncOpenAI

from customer_service_agent.core.config import get_settings


class EmbeddingService:
    """Create embeddings for text"""

    def __init__(self, client: AsyncOpenAI | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self._model = model or settings.embedding_model
        self._client = client or AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Convert text to embeddings"""
        if not texts:
            return []

        response = await self._client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]

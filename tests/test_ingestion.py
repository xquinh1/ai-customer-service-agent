import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from customer_service_agent.core.config import get_settings
from customer_service_agent.db.models import Document, DocumentChunk
from customer_service_agent.knowledge.fetcher import FetchResult
from customer_service_agent.knowledge.ingestion import ingest_url


class FakeFetcher:
    """Tra HTML co dinh - khong goi mang that."""

    def __init__(self, html: str) -> None:
        self.html = html

    async def fetch(self, url: str) -> FetchResult:
        return FetchResult(
            url=url,
            final_url=url,
            content_type="text/html",
            content=self.html,
        )


class FakeEmbedder:
    """Tra vector gia 1536 chieu - khong goi OpenAI that."""

    _model = "fake-model"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 1536 for _ in texts]


SAMPLE_HTML = """
<article>
  <h1>Creating discount codes</h1>
  <p>You can create discount codes from your admin.</p>
  <h2>Steps</h2>
  <p>Open the Discounts page and click Create.</p>
</article>
"""

CHANGED_HTML = """
<article>
  <h1>Creating discount codes</h1>
  <p>This is UPDATED content about discount codes.</p>
  <h2>Steps</h2>
  <p>Open the Discounts page and click Create.</p>
</article>
"""

TEST_URL = "https://help.shopify.com/manual/ingest-test"


@asynccontextmanager
async def _session() -> AsyncIterator[AsyncSession]:
    """Mo session bang engine RIENG, tu dong dispose khi xong.

    asyncio.run tao event loop moi moi lan goi - khong duoc dung engine
    chung cua app (no gan voi loop cua TestClient o conftest.py).
    """
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


def test_ingest_creates_document_and_chunks() -> None:
    async def scenario() -> tuple[Document, list[DocumentChunk]]:
        async with _session() as session:
            # Don dep du lieu test cu (idempotent - test chay lai duoc)
            await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == TEST_URL))
            await session.execute(delete(Document).where(Document.url == TEST_URL))

            document = await ingest_url(
                TEST_URL,
                session=session,
                fetcher=FakeFetcher(SAMPLE_HTML),  # type: ignore[arg-type]
                embedder=FakeEmbedder(),  # type: ignore[arg-type]
            )

            result = await session.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document.id)
                .order_by(DocumentChunk.chunk_index)
            )
            chunks = list(result.scalars().all())
            return document, chunks

    document, chunks = asyncio.run(scenario())

    assert document.url == TEST_URL
    assert len(chunks) == 2
    assert chunks[0].title == "Creating discount codes"
    assert chunks[0].chunk_index == 0
    assert chunks[0].embedding is not None
    assert len(chunks[0].embedding) == 1536


def test_ingest_same_content_does_not_create_duplicates() -> None:
    async def scenario() -> int:
        async with _session() as session:
            # Chay lan 1: tao moi
            await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == TEST_URL))
            await session.execute(delete(Document).where(Document.url == TEST_URL))
            await ingest_url(
                TEST_URL,
                session=session,
                fetcher=FakeFetcher(SAMPLE_HTML),  # type: ignore[arg-type]
                embedder=FakeEmbedder(),  # type: ignore[arg-type]
            )

            # Chay lan 2: noi dung KHONG DOI -> phai bo qua (idempotent)
            await ingest_url(
                TEST_URL,
                session=session,
                fetcher=FakeFetcher(SAMPLE_HTML),  # type: ignore[arg-type]
                embedder=FakeEmbedder(),  # type: ignore[arg-type]
            )

            result = await session.execute(select(Document).where(Document.url == TEST_URL))
            documents = list(result.scalars().all())
            return len(documents)

    assert asyncio.run(scenario()) == 1


def test_ingest_changed_content_updates_document() -> None:
    async def scenario() -> tuple[int, int, str]:
        async with _session() as session:
            await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == TEST_URL))
            await session.execute(delete(Document).where(Document.url == TEST_URL))

            # Lan 1: noi dung cu
            await ingest_url(
                TEST_URL,
                session=session,
                fetcher=FakeFetcher(SAMPLE_HTML),  # type: ignore[arg-type]
                embedder=FakeEmbedder(),  # type: ignore[arg-type]
            )

            # Lan 2: noi dung DOI (UPDATED) -> cap nhat, khong tao moi
            updated = await ingest_url(
                TEST_URL,
                session=session,
                fetcher=FakeFetcher(CHANGED_HTML),  # type: ignore[arg-type]
                embedder=FakeEmbedder(),  # type: ignore[arg-type]
            )

            result = await session.execute(select(Document).where(Document.url == TEST_URL))
            document_count = len(list(result.scalars().all()))

            chunk_result = await session.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == updated.id)
            )
            chunk_count = len(list(chunk_result.scalars().all()))

            return document_count, chunk_count, updated.content

    document_count, chunk_count, content = asyncio.run(scenario())

    assert document_count == 1  # van 1 document - khong tao moi
    assert chunk_count == 2  # chunk cu da xoa, chunk moi thay the
    assert "UPDATED" in content  # noi dung moi da duoc luu

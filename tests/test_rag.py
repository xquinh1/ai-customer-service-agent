import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from customer_service_agent.core.config import get_settings
from customer_service_agent.db.models import Document, DocumentChunk
from customer_service_agent.rag.context_builder import build_context
from customer_service_agent.rag.fusion import reciprocal_rank_fusion
from customer_service_agent.rag.reranking import rerank
from customer_service_agent.rag.retrieval import lexical_search


def _chunk(title: str) -> DocumentChunk:
    return DocumentChunk(
        id=uuid4(),
        content=title,
        source_url="https://u",
        title=title,
        content_hash=f"hash-{title}",
    )


class _FakeChatClient:
    """Gia lap client OpenAI - tra ve JSON do MINH quyet dinh, khong goi API that."""

    def __init__(self, payload: str) -> None:
        self._payload = payload
        self.requests: list[dict[str, object]] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    async def _create(self, **kwargs: object) -> object:
        self.requests.append(kwargs)
        message = SimpleNamespace(content=self._payload)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_build_context_numbers_chunks_and_keeps_citations() -> None:
    chunks = [
        DocumentChunk(
            content="Open the Orders page.",
            source_url="https://a",
            title="Refunds",
            content_hash="hash-1",
        ),
        DocumentChunk(
            content="Click Refund.", source_url="https://b", title=None, content_hash="hash-2"
        ),
    ]

    context, citations = build_context(chunks)

    assert context == "[1] Open the Orders page.\n[2] Click Refund."
    assert citations == [
        {"title": "Refunds", "url": "https://a"},
        {"title": "", "url": "https://b"},
    ]


def test_rrf_ranks_chunk_present_in_both_lists_first() -> None:
    a, b, c = _chunk("A"), _chunk("B"), _chunk("C")

    merged = reciprocal_rank_fusion([(a, 0.42), (b, 0.68)], [(b, 0.06), (c, 0.03)])

    assert [chunk.title for chunk in merged] == ["B", "A", "C"]


def test_rrf_ignores_raw_scores_and_uses_positions() -> None:
    a, b = _chunk("A"), _chunk("B")

    # A co "diem" tot hon o ca 2 ben NHUNG bi xep hang 2 -> RRF chi nhin VI TRI
    merged = reciprocal_rank_fusion([(b, 999.0), (a, 0.001)], [(b, 500.0), (a, 0.002)])

    assert [chunk.title for chunk in merged] == ["B", "A"]


TEST_URL = "https://help.shopify.com/test/rag-retrieval"

CHUNKS = [
    ("Refunding orders", "To refund an order, go to the Orders page and click Refund."),
    ("Creating discount codes", "You can create discount codes from the Discounts page."),
    ("Discount code examples", "The code SAVE10 gives customers 10 percent off."),
    ("Shopify Payments", "Shopify Payments lets you accept credit cards."),
]


@asynccontextmanager
async def _session() -> AsyncIterator[AsyncSession]:
    """Session voi engine rieng (tranh xung dot event loop - bai hoc L6)."""
    engine = create_async_engine(get_settings().database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


async def _seed(session: AsyncSession) -> None:
    """Tao 4 chunk voi embedding GIA (lexical khong dung embedding)."""
    await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == TEST_URL))
    await session.execute(delete(Document).where(Document.url == TEST_URL))

    document = Document(
        url=TEST_URL,
        title="Retrieval test",
        source="test",
        content="test",
        content_hash="test",
    )
    session.add(document)
    await session.flush()

    for index, (title, content) in enumerate(CHUNKS):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                title=title,
                content=content,
                source_url=TEST_URL,
                content_hash="test",
                embedding=[0.1] * 1536,
                embedding_model="fake",
            )
        )
    await session.commit()


async def _cleanup(session: AsyncSession) -> None:
    await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == TEST_URL))
    await session.execute(delete(Document).where(Document.url == TEST_URL))
    await session.commit()


def test_lexical_search_finds_exact_token() -> None:
    async def scenario() -> list[str | None]:
        async with _session() as session:
            await _seed(session)
            found = await lexical_search(session, "SAVE10", limit=3)
            await _cleanup(session)
            return [chunk.title for chunk, _rank in found]

    assert asyncio.run(scenario()) == ["Discount code examples"]


def test_lexical_search_returns_nothing_without_shared_words() -> None:
    async def scenario() -> list[str | None]:
        async with _session() as session:
            await _seed(session)
            found = await lexical_search(session, "give customers their money back", limit=3)
            await _cleanup(session)
            return [chunk.title for chunk, _rank in found]

    assert asyncio.run(scenario()) == []


def test_rerank_orders_by_score() -> None:
    a, b, c = _chunk("A"), _chunk("B"), _chunk("C")
    fake = _FakeChatClient(
        '{"scores": [{"index": 1, "score": 2}, {"index": 2, "score": 9}, {"index": 3, "score": 5}]}'
    )

    ranked = asyncio.run(
        rerank("q", [a, b, c], client=fake, model="fake", limit=2)  # type: ignore[arg-type]
    )

    assert [item.chunk.title for item in ranked] == ["B", "C"]
    assert [item.relevance_score for item in ranked] == [9.0, 5.0]


def test_rerank_skips_invalid_scores() -> None:
    a, b = _chunk("A"), _chunk("B")
    fake = _FakeChatClient(
        '{"scores": [{"index": 1, "score": 7}, {"index": 99, "score": 10},'
        ' {"index": 2, "score": "high"}, {"index": 0, "score": 5}]}'
    )

    ranked = asyncio.run(
        rerank("q", [a, b], client=fake, model="fake", limit=5)  # type: ignore[arg-type]
    )

    assert [item.chunk.title for item in ranked] == ["A"]


def test_rerank_returns_empty_without_candidates() -> None:
    fake = _FakeChatClient('{"scores": []}')

    ranked = asyncio.run(
        rerank("q", [], client=fake, model="fake")  # type: ignore[arg-type]
    )

    assert ranked == []
    assert fake.requests == []

import asyncio

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from customer_service_agent.core.config import get_settings
from customer_service_agent.db.models import Document, DocumentChunk
from customer_service_agent.knowledge.embeddings import EmbeddingService

EVAL_URL = "https://help.shopify.com/eval/retrieval"

KB: list[tuple[str, str]] = [
    ("Refunding orders", "To refund an order, open the Orders page and click Refund."),
    ("Creating discount codes", "Create discount codes from the Discounts page in admin."),
    ("Discount code examples", "The code SAVE10 gives 10 percent off. FREESHIP removes shipping."),
    ("Shopify Payments", "Shopify Payments lets you accept credit cards and local methods."),
    ("Shipping zones", "Configure shipping zones and rates in Settings > Shipping."),
    ("Product visibility", "If a product is not appearing, check its sales channel availability."),
    (
        "Changing store currency",
        "Change currency in Settings > Store details before your first sale.",
    ),
    ("Adding products", "Add products from the Products page, with variants and images."),
]

GOLDEN: list[tuple[str, str]] = [
    ("How do I give a customer their money back?", "Refunding orders"),
    ("What does the code SAVE10 do?", "Discount code examples"),
    ("My product is not showing up in my store", "Product visibility"),
    ("How can I accept credit cards?", "Shopify Payments"),
    ("How do I set up shipping rates?", "Shipping zones"),
    ("How can I change the currency of my store?", "Changing store currency"),
    ("How do I put a new item up for sale?", "Adding products"),
    ("Does FREESHIP remove shipping costs?", "Discount code examples"),
]


async def _cleanup(session: AsyncSession) -> None:
    """Xoa sach du lieu eval khoi DB (de chay lai nhieu lan van dung)."""
    await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == EVAL_URL))
    await session.execute(delete(Document).where(Document.url == EVAL_URL))
    await session.commit()


async def _seed(session: AsyncSession, embedder: EmbeddingService) -> None:
    """Nap 8 chunk KB vao DB voi embedding THAT."""
    await _cleanup(session)

    document = Document(
        url=EVAL_URL,
        title="Retrieval eval",
        source="eval",
        content="eval",
        content_hash="eval",
    )
    session.add(document)
    await session.flush()

    vectors = await embedder.embed([content for _title, content in KB])
    for index, ((title, content), vector) in enumerate(zip(KB, vectors, strict=True)):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                title=title,
                content=content,
                source_url=EVAL_URL,
                content_hash=f"eval-{index}",
                embedding=vector,
                embedding_model="eval",
            )
        )
    await session.commit()


def _hit_at_k(ranks: list[int], k: int) -> float:
    """Ti le cau ma chunk dung nam trong top-k."""
    hits = sum(1 for r in ranks if 1 <= r <= k)
    return hits / len(ranks)


def _mrr(ranks: list[int]) -> float:
    """Mean Reciprocal Rank: trung binh 1/vi_tri (vi_tri 1 = 1.0, vi_tri 2 = 0.5...)."""
    total = 0.0
    for r in ranks:
        if r >= 1:
            total += 1.0 / r
    return total / len(ranks)


async def _semantic_search(
    session: AsyncSession, query: str, embedder: EmbeddingService, limit: int = 3
) -> list[str]:
    """Tim kiem chi semantic (vector)."""
    from customer_service_agent.rag.retrieval import search_chunks

    if not query or not query.strip():
        return []
    vector = (await embedder.embed([query]))[0]
    chunks = await search_chunks(session, vector, limit=limit)
    return [c.title for c, _ in chunks]


async def _hybrid_search_fn(
    session: AsyncSession, query: str, embedder: EmbeddingService, limit: int = 3
) -> list[str]:
    """Tim kiem hybrid (semantic + lexical + RRF)."""
    from customer_service_agent.rag.fusion import hybrid_search

    if not query or not query.strip():
        return []
    chunks = await hybrid_search(session, query, embedder=embedder, limit=limit, candidate_limit=10)
    return [c.title for c in chunks]


async def _hybrid_rerank_search(
    session: AsyncSession,
    query: str,
    embedder: EmbeddingService,
    client,
    model: str,
    limit: int = 3,
) -> list[str]:
    """Tim kiem hybrid + rerank."""
    from customer_service_agent.rag.fusion import hybrid_search
    from customer_service_agent.rag.reranking import rerank

    if not query or not query.strip():
        return []
    candidates = await hybrid_search(
        session, query, embedder=embedder, limit=limit * 2, candidate_limit=10
    )
    ranked = await rerank(query, candidates, client=client, model=model, limit=limit)
    return [item.chunk.title for item in ranked]


async def _run_config(
    name: str, search_fn, session, embedder, *extra_args
) -> tuple[float, float, float]:
    """Chay 1 cau hinh tren tat ca GOLDEN, tra ve (hit@1, hit@3, MRR)."""
    ranks = []
    for query, expected_title in GOLDEN:
        results = await search_fn(session, query, embedder, *extra_args)
        try:
            rank = results.index(expected_title) + 1
        except ValueError:
            rank = 0
        ranks.append(rank)

    return _hit_at_k(ranks, 1), _hit_at_k(ranks, 3), _mrr(ranks)


async def main() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    embedder = EmbeddingService()
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    async with factory() as session:
        await _seed(session, embedder)

        # A. Semantic only
        h1, h3, mrr = await _run_config(
            "Semantic only",
            _semantic_search,
            session,
            embedder,
        )
        print(f"[A] Semantic only   : hit@1={h1:.2f}  hit@3={h3:.2f}  MRR={mrr:.3f}")

        # B. Hybrid (RRF)
        h1, h3, mrr = await _run_config(
            "Hybrid (RRF)",
            _hybrid_search_fn,
            session,
            embedder,
        )
        print(f"[B] Hybrid (RRF)    : hit@1={h1:.2f}  hit@3={h3:.2f}  MRR={mrr:.3f}")

        # C. Hybrid + Rerank
        h1, h3, mrr = await _run_config(
            "Hybrid + Rerank",
            _hybrid_rerank_search,
            session,
            embedder,
            client,
            settings.chat_model,
        )
        print(f"[C] Hybrid+Rerank   : hit@1={h1:.2f}  hit@3={h3:.2f}  MRR={mrr:.3f}")

        await _cleanup(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

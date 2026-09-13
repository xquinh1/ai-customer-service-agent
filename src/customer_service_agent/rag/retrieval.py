from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_service_agent.db.models import DocumentChunk


async def search_chunks(
    session: AsyncSession,
    query_vector: list[float],
    limit: int = 5,
) -> list[tuple[DocumentChunk, float]]:
    """Find the K chunks closest to query_vector based on cosine distance."""
    distance = DocumentChunk.embedding.cosine_distance(query_vector)
    result = await session.execute(
        select(DocumentChunk, distance.label("distance"))
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    )
    return [(chunk, dist) for chunk, dist in result.all()]


async def lexical_search(
    session: AsyncSession,
    query: str,
    limit: int = 5,
) -> list[tuple[DocumentChunk, float]]:
    """using postgresql full-text search to find chunk"""

    tsvector = func.to_tsvector("english", DocumentChunk.content)
    tsquery = func.plainto_tsquery("english", query)
    rank = func.ts_rank(tsvector, tsquery).label("rank")

    result = await session.execute(
        select(DocumentChunk, rank)
        .where(tsvector.op("@@")(tsquery))
        .order_by(rank.desc())
        .limit(limit)
    )
    return [(chunk, float(r)) for chunk, r in result.all()]

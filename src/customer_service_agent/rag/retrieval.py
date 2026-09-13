from sqlalchemy import select
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

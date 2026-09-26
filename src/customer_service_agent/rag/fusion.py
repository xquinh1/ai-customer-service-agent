from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from customer_service_agent.db.models import DocumentChunk
from customer_service_agent.knowledge.embeddings import EmbeddingService
from customer_service_agent.rag.retrieval import lexical_search, search_chunks


def reciprocal_rank_fusion(
    semantic: list[tuple[DocumentChunk, float]],
    lexical: list[tuple[DocumentChunk, float]],
    k: int = 60,
) -> list[DocumentChunk]:
    """RRF:  Combine two ranking lists based on POSITION (not score).
    score(chunk) = sum(1/(k+rank)) across all lists containing that chunk.
    k=60 (the default from the RRF paper) reduces the influence of top-ranked items.
    """
    scores: dict[UUID, float] = {}
    chunks_by_id: dict[UUID, DocumentChunk] = {}

    for results in (semantic, lexical):
        for rank, (chunk, _score) in enumerate(results, start=1):
            chunks_by_id[chunk.id] = chunk
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1.0 / (k + rank)

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [chunks_by_id[chunk_id] for chunk_id, _score in ordered]


async def hybrid_search(
    session: AsyncSession,
    query: str,
    embedder: EmbeddingService,
    limit: int = 5,
    candidate_limit: int = 10,
) -> list[DocumentChunk]:
    """Chay CA semantic + lexical, gop bang RRF (requirements muc 21).

    candidate_limit > limit: lay nhieu ung vien tu moi ben de fusion co
    nhieu "y kien" hon, sau do cat con limit ket qua cuoi.
    """
    query_vector = (await embedder.embed([query]))[0]

    semantic = await search_chunks(session, query_vector, limit=candidate_limit)
    lexical = await lexical_search(session, query, limit=candidate_limit)

    return reciprocal_rank_fusion(semantic, lexical)[:limit]

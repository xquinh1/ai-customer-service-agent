import hashlib

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_service_agent.db.models import Document, DocumentChunk
from customer_service_agent.knowledge.chunker import chunk_blocks
from customer_service_agent.knowledge.cleaner import clean_blocks
from customer_service_agent.knowledge.embeddings import EmbeddingService
from customer_service_agent.knowledge.fetcher import SafeFetcher
from customer_service_agent.knowledge.parser import parse_html


def content_hash(text: str) -> str:
    """for check if the same content"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def ingest_url(
    url: str,
    session: AsyncSession,
    embedder: EmbeddingService | None = None,
    fetcher: SafeFetcher | None = None,
) -> Document:
    """Fetch, parse, clean, chunk, embed and save url"""
    fetcher = fetcher or SafeFetcher()
    embedder = embedder or EmbeddingService()

    fetched = await fetcher.fetch(url)
    parsed = parse_html(fetched.content)
    blocks = clean_blocks(parsed.blocks)

    chunks = chunk_blocks(blocks)

    full_text = "\n".join(block.text for block in blocks)
    digest = content_hash(full_text)

    existing = await session.scalar(select(Document).where(Document.url == url))

    if existing is not None and existing.content_hash == digest:
        return existing
    if existing is None:
        document = Document(
            url=url,
            title=parsed.title,
            source="shopify-help-center",
            content=full_text,
            content_hash=digest,
        )
        session.add(document)
    else:
        document = existing
        document.title = parsed.title
        document.content = full_text
        document.content_hash = digest
        await session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))

    await session.flush()

    texts = [chunk.content for chunk in chunks]
    vectors = await embedder.embed(texts)

    for index, (chunk, vector) in enumerate(zip(chunks, vectors, strict=True)):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                title=chunk.title,
                content=chunk.content,
                source_url=url,
                content_hash=content_hash(chunk.content),
                embedding=vector,
                embedding_model=embedder._model,
            )
        )

    await session.commit()
    return document

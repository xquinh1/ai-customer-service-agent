"""Demo pgvector: luu embedding that + tim kiem gan nghia."""

import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from customer_service_agent.core.config import get_settings
from customer_service_agent.db.models import Document, DocumentChunk


async def setup_data() -> None:
    engine = create_async_engine(get_settings().database_url)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    contents = [
        "You can create discount codes from the Discounts page in your Shopify admin.",
        "To refund an order, go to Orders and click Refund on the order page.",
        "Shopify Payments lets you accept credit cards directly in your store.",
    ]

    async with Session() as session:
        # Xoa du lieu demo cu (neu co) de chay lai duoc (idempotent)
        from sqlalchemy import delete

        demo_url = "https://help.shopify.com/manual/demo"
        await session.execute(delete(DocumentChunk).where(DocumentChunk.source_url == demo_url))
        await session.execute(delete(Document).where(Document.url == demo_url))

        doc = Document(
            url=demo_url,
            title="Demo page",
            source="shopify-help-center",
            content="\n".join(contents),
            content_hash="demo-hash",
        )
        session.add(doc)
        await session.flush()

        for index, text in enumerate(contents):
            session.add(
                DocumentChunk(
                    document_id=doc.id,
                    chunk_index=index,
                    content=text,
                    source_url=doc.url,
                    content_hash=f"demo-{index}",
                )
            )
        await session.commit()
        print("Inserted document + 3 chunks (chua co embedding)")
    await engine.dispose()


async def embed_and_search() -> None:
    """Embed cac chunk, roi tim chunk gan nhat voi cau hoi."""
    from sqlalchemy import select

    from customer_service_agent.knowledge.embeddings import EmbeddingService

    engine = create_async_engine(get_settings().database_url)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    svc = EmbeddingService()

    async with Session() as session:
        # Lay cac chunk cua document demo
        chunks = (
            (
                await session.execute(
                    select(DocumentChunk).where(
                        DocumentChunk.source_url == "https://help.shopify.com/manual/demo"
                    )
                )
            )
            .scalars()
            .all()
        )

        # Tao embedding cho tung chunk bang EmbeddingService
        texts = [chunk.content for chunk in chunks]
        vectors = await svc.embed(texts)
        for chunk, vector in zip(chunks, vectors, strict=True):
            chunk.embedding = vector
            chunk.embedding_model = svc._model
        await session.commit()
        print(f"Embedded {len(chunks)} chunks (1536 chieu moi chunk)")

        # CAU HOI: embed roi tim chunk gan nhat qua cosine distance
        question = "How do I give my customers a discount?"
        question_vector = (await svc.embed([question]))[0]

        # cosine_distance() cua pgvector tu ma hoa list -> vector
        distance = DocumentChunk.embedding.cosine_distance(question_vector)
        rows = (
            await session.execute(
                select(DocumentChunk.content, distance.label("distance"))
                .order_by(distance)
                .limit(3)
            )
        ).all()
        print("\n=== Cau hoi:", question, "===")
        for content, dist in rows:
            print(f"  distance={dist:.4f} | {content[:60]}")
    await engine.dispose()


async def main() -> None:
    await setup_data()
    await embed_and_search()


asyncio.run(main())

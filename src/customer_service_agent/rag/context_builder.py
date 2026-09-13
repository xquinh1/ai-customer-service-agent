from customer_service_agent.db.models import DocumentChunk


def build_context(chunks: list[tuple[DocumentChunk, float]]) -> tuple[str, list[dict[str, str]]]:
    """Convert chunks into the context for LLM + a list of citations
    Return (context_text, citations)
    Context_text: chunks numbered [1], [2]... for the LLM
    Citations: list of {title, url} objects in the corresponding order
    """
    parts: list[str] = []
    citations: list[dict[str, str]] = []
    for index, (chunk, _distance) in enumerate(chunks, start=1):
        parts.append(f"[{index}] {chunk.content}")
        citations.append({"title": chunk.title or "", "url": chunk.source_url})

    return "\n".join(parts), citations

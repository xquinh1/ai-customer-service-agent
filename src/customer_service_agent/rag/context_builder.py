import tiktoken

from customer_service_agent.db.models import DocumentChunk

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    """count token exactly by usung tiktoken (OpenAI encoding)."""
    return len(_ENCODER.encode(text))


def build_context(
    chunks: list[DocumentChunk],
    max_tokens: int = 4000,
) -> tuple[str, list[dict[str, str]]]:
    """buiding context for LLM: dedupe + token budget + numbering + citations."""
    # 1. DEDUPE
    seen_hashes: set[str] = set()
    unique_chunks: list[DocumentChunk] = []
    for chunk in chunks:
        if chunk.content_hash not in seen_hashes:
            seen_hashes.add(chunk.content_hash)
            unique_chunks.append(chunk)

    # 2. TOKEN BUDGET
    context_parts: list[str] = []
    citations: list[dict[str, str]] = []
    used_tokens = 0

    for index, chunk in enumerate(unique_chunks, start=1):
        chunk_text = f"[{index}] {chunk.content}"
        chunk_tokens = _count_tokens(chunk_text)

        if used_tokens + chunk_tokens > max_tokens:
            break

        context_parts.append(chunk_text)
        citations.append({"title": chunk.title or "", "url": chunk.source_url})
        used_tokens += chunk_tokens

    return "\n".join(context_parts), citations

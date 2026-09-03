from dataclasses import dataclass

from customer_service_agent.knowledge.parser import ParsedBlock


@dataclass
class Chunk:
    title: str
    content: str


def chunk_blocks(blocks: list[ParsedBlock], max_chars: int = 2000) -> list[Chunk]:
    """Cut blocks into chunk by section
    Meet heading -> start the new chunk with the heading's text title
    Paragraph/li -> added to the current chunk.
    """
    chunks: list[Chunk] = []
    current_title = ""
    current_parts: list[str] = []
    for block in blocks:
        if block.kind == "heading":
            if current_parts:
                chunks.append(Chunk(title=current_title, content="\n".join(current_parts)))
            current_title = block.text
            current_parts = []
        else:
            if current_parts and len("\n".join(current_parts)) + len(block.text) > max_chars:
                chunks.append(Chunk(title=current_title, content="\n".join(current_parts)))
                current_parts = []
            current_parts.append(block.text)

    if current_parts:
        chunks.append(Chunk(title=current_title, content="\n".join(current_parts)))
    return chunks

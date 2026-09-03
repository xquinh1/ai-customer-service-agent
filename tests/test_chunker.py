from customer_service_agent.knowledge.chunker import chunk_blocks
from customer_service_agent.knowledge.parser import ParsedBlock


def _blocks(*items: tuple[str, int, str]) -> list[ParsedBlock]:
    return [ParsedBlock(kind=kind, level=level, text=text) for kind, level, text in items]


def test_group_blocks_by_heading() -> None:
    blocks = _blocks(
        ("heading", 1, "Creating discount codes"),
        ("paragraph", 0, "Go to Discounts in your admin."),
        ("heading", 2, "Setting limits"),
        ("paragraph", 0, "Set a minimum order value."),
    )

    chunks = chunk_blocks(blocks)

    assert len(chunks) == 2
    assert chunks[0].title == "Creating discount codes"
    assert chunks[1].title == "Setting limits"
    assert chunks[1].content == "Set a minimum order value."


def test_split_chunk_when_over_max_chars() -> None:
    blocks = _blocks(
        ("heading", 1, "Refunds"),
        ("paragraph", 0, "You can refund orders."),
        ("paragraph", 0, "Open the Orders page."),
    )

    chunks = chunk_blocks(blocks, max_chars=30)

    assert len(chunks) == 2
    assert chunks[0].content == "You can refund orders."
    assert chunks[1].content == "Open the Orders page."


def test_last_chunk_is_not_lost() -> None:
    blocks = _blocks(
        ("heading", 1, "Refunds"),
        ("paragraph", 0, "You can refund orders."),
    )

    chunks = chunk_blocks(blocks)

    assert len(chunks) == 1
    assert chunks[0].content == "You can refund orders."
